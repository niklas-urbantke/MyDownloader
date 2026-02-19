#pragma once

#include <string>
#include <functional>
#include <memory>
#include <thread>
#include <atomic>

/**
 * Download configuration
 */
struct DownloadConfig
{
    std::string url;
    std::string outputPath;
    std::string format;          // mp3, m4a, opus, flac, wav
    int quality;                 // 0-9 (0 = best, 9 = smallest)
    bool downloadPlaylist;
    bool embedThumbnail;
    bool embedMetadata;
    bool downloadSubtitles;
    std::string subtitleLanguage;
    int speedLimit;              // KB/s, 0 = unlimited
    bool keepVideo;
};

/**
 * Download progress callback
 */
using ProgressCallback = std::function<void(int percent, const std::string& status, const std::string& details)>;
using CompletionCallback = std::function<void(bool success, const std::string& message)>;
using LogCallback = std::function<void(const std::string& message)>;

/**
 * Downloader class - Manages downloads using yt-dlp
 */
class Downloader
{
public:
    Downloader();
    ~Downloader();

    // Download control
    void Download(const DownloadConfig& config);
    void Cancel();
    void Pause();
    void Resume();
    
    // Status
    bool IsDownloading() const { return m_isDownloading; }
    bool IsPaused() const { return m_isPaused; }
    
    // Callbacks
    void SetProgressCallback(ProgressCallback callback) { m_progressCallback = callback; }
    void SetCompletionCallback(CompletionCallback callback) { m_completionCallback = callback; }
    void SetLogCallback(LogCallback callback) { m_logCallback = callback; }
    
    // Utilities
    static bool CheckYtDlpInstalled();
    static bool CheckFfmpegInstalled();
    static std::string GetVideoInfo(const std::string& url);

private:
    std::atomic<bool> m_isDownloading;
    std::atomic<bool> m_isPaused;
    std::atomic<bool> m_shouldCancel;
    
    std::unique_ptr<std::thread> m_downloadThread;
    
    ProgressCallback m_progressCallback;
    CompletionCallback m_completionCallback;
    LogCallback m_logCallback;
    
    // Helper methods
    void DownloadThread(const DownloadConfig& config);
    std::string BuildYtDlpCommand(const DownloadConfig& config);
    void ParseProgress(const std::string& output);
    void Log(const std::string& message);
};
