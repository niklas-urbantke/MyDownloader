#include "core/downloader.h"
#include "utils/file_utils.h"
#include "utils/string_utils.h"
#include <cstdlib>
#include <sstream>
#include <array>
#include <memory>

#ifdef _WIN32
#include <windows.h>
#define popen _popen
#define pclose _pclose
#endif

Downloader::Downloader()
    : m_isDownloading(false),
      m_isPaused(false),
      m_shouldCancel(false)
{
}

Downloader::~Downloader()
{
    Cancel();
    if (m_downloadThread && m_downloadThread->joinable())
    {
        m_downloadThread->join();
    }
}

void Downloader::Download(const DownloadConfig& config)
{
    if (m_isDownloading)
    {
        Log("Download already in progress!");
        return;
    }
    
    m_shouldCancel = false;
    m_downloadThread = std::make_unique<std::thread>(&Downloader::DownloadThread, this, config);
}

void Downloader::Cancel()
{
    m_shouldCancel = true;
}

void Downloader::Pause()
{
    m_isPaused = true;
}

void Downloader::Resume()
{
    m_isPaused = false;
}

void Downloader::DownloadThread(const DownloadConfig& config)
{
    m_isDownloading = true;
    
    std::string command = BuildYtDlpCommand(config);
    Log("Executing: " + command);
    
    FILE* pipe = popen(command.c_str(), "r");
    if (!pipe)
    {
        if (m_completionCallback)
            m_completionCallback(false, "Failed to start download process");
        m_isDownloading = false;
        return;
    }
    
    char buffer[256];
    while (fgets(buffer, sizeof(buffer), pipe) != nullptr)
    {
        if (m_shouldCancel)
        {
            pclose(pipe);
            if (m_completionCallback)
                m_completionCallback(false, "Download canceled");
            m_isDownloading = false;
            return;
        }
        
        std::string output(buffer);
        ParseProgress(output);
        Log(output);
    }
    
    int returnCode = pclose(pipe);
    
    if (returnCode == 0)
    {
        if (m_completionCallback)
            m_completionCallback(true, "Download completed successfully");
    }
    else
    {
        if (m_completionCallback)
            m_completionCallback(false, "Download failed with error code: " + std::to_string(returnCode));
    }
    
    m_isDownloading = false;
}

std::string Downloader::BuildYtDlpCommand(const DownloadConfig& config)
{
    std::ostringstream cmd;
    cmd << "yt-dlp";
    
    // Output path
    if (!config.outputPath.empty())
    {
        cmd << " -o \"" << config.outputPath << "/%(title)s.%(ext)s\"";
    }
    
    // Extract audio
    cmd << " -x --audio-format " << config.format;
    cmd << " --audio-quality " << config.quality;
    
    // Thumbnail
    if (config.embedThumbnail)
    {
        cmd << " --embed-thumbnail";
    }
    
    // Metadata
    if (config.embedMetadata)
    {
        cmd << " --embed-metadata";
    }
    
    // Playlist
    if (!config.downloadPlaylist)
    {
        cmd << " --no-playlist";
    }
    
    // Subtitles
    if (config.downloadSubtitles)
    {
        cmd << " --write-subs --sub-langs " << config.subtitleLanguage;
    }
    
    // Speed limit
    if (config.speedLimit > 0)
    {
        cmd << " --limit-rate " << config.speedLimit << "K";
    }
    
    // Progress
    cmd << " --newline --progress";
    
    // URL
    cmd << " \"" << config.url << "\"";
    
    return cmd.str();
}

void Downloader::ParseProgress(const std::string& output)
{
    // Parse yt-dlp progress output
    // Format: [download] 45.3% of 10.5MiB at 1.2MiB/s ETA 00:05
    
    if (output.find("[download]") != std::string::npos)
    {
        size_t percentPos = output.find('%');
        if (percentPos != std::string::npos)
        {
            // Extract percentage
            size_t start = output.rfind(' ', percentPos) + 1;
            std::string percentStr = output.substr(start, percentPos - start);
            
            try
            {
                double percent = std::stod(percentStr);
                if (m_progressCallback)
                {
                    m_progressCallback(static_cast<int>(percent), "Downloading", output);
                }
            }
            catch (...) {}
        }
    }
}

void Downloader::Log(const std::string& message)
{
    if (m_logCallback)
    {
        m_logCallback(message);
    }
}

bool Downloader::CheckYtDlpInstalled()
{
    #ifdef _WIN32
    int result = system("where yt-dlp >nul 2>&1");
    #else
    int result = system("which yt-dlp >/dev/null 2>&1");
    #endif
    return result == 0;
}

bool Downloader::CheckFfmpegInstalled()
{
    #ifdef _WIN32
    int result = system("where ffmpeg >nul 2>&1");
    #else
    int result = system("which ffmpeg >/dev/null 2>&1");
    #endif
    return result == 0;
}

std::string Downloader::GetVideoInfo(const std::string& url)
{
    std::string command = "yt-dlp --dump-json \"" + url + "\"";
    
    FILE* pipe = popen(command.c_str(), "r");
    if (!pipe) return "";
    
    std::string result;
    char buffer[256];
    while (fgets(buffer, sizeof(buffer), pipe) != nullptr)
    {
        result += buffer;
    }
    
    pclose(pipe);
    return result;
}
