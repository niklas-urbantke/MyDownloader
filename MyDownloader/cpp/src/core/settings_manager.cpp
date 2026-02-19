#include "core/settings_manager.h"
#include "utils/file_utils.h"
#include <fstream>

#ifdef _WIN32
#include <shlobj.h>
#include <windows.h>
#else
#include <unistd.h>
#include <pwd.h>
#endif

SettingsManager::SettingsManager()
{
    m_settingsPath = GetSettingsPath();
    LoadDefaults();
}

SettingsManager::~SettingsManager()
{
}

void SettingsManager::Load()
{
    if (!FileUtils::FileExists(m_settingsPath))
    {
        LoadDefaults();
        return;
    }
    
    try
    {
        std::string content = FileUtils::ReadFile(m_settingsPath);
        json j = json::parse(content);
        FromJson(j);
    }
    catch (const std::exception& e)
    {
        LoadDefaults();
    }
}

void SettingsManager::Save()
{
    try
    {
        json j = ToJson();
        std::string content = j.dump(4);
        FileUtils::WriteFile(m_settingsPath, content);
    }
    catch (const std::exception& e)
    {
        // Error saving
    }
}

void SettingsManager::Reset()
{
    LoadDefaults();
    Save();
}

void SettingsManager::LoadDefaults()
{
#ifdef _WIN32
    char path[MAX_PATH];
    if (SHGetFolderPathA(NULL, CSIDL_MYDOCUMENTS, NULL, 0, path) == S_OK)
    {
        m_downloadFolder = std::string(path) + "\\MyDownloader\\Songs";
    }
    else
    {
        m_downloadFolder = "C:\\Users\\Public\\Music\\MyDownloader";
    }
#else
    const char* home = getenv("HOME");
    if (!home)
    {
        struct passwd* pw = getpwuid(getuid());
        home = pw->pw_dir;
    }
    m_downloadFolder = std::string(home) + "/Music/MyDownloader";
#endif
    
    m_audioFormat = "mp3";
    m_audioQuality = 0;
    m_embedThumbnail = true;
    m_embedMetadata = true;
    m_downloadSubtitles = false;
    m_subtitleLanguage = "de,en";
    m_speedLimit = 0;
    m_theme = "System";
    m_autoQueue = false;
    m_keepVideo = false;
}

json SettingsManager::ToJson() const
{
    json j;
    j["downloadFolder"] = m_downloadFolder;
    j["audioFormat"] = m_audioFormat;
    j["audioQuality"] = m_audioQuality;
    j["embedThumbnail"] = m_embedThumbnail;
    j["embedMetadata"] = m_embedMetadata;
    j["downloadSubtitles"] = m_downloadSubtitles;
    j["subtitleLanguage"] = m_subtitleLanguage;
    j["speedLimit"] = m_speedLimit;
    j["theme"] = m_theme;
    j["autoQueue"] = m_autoQueue;
    j["keepVideo"] = m_keepVideo;
    return j;
}

void SettingsManager::FromJson(const json& j)
{
    if (j.contains("downloadFolder")) m_downloadFolder = j["downloadFolder"];
    if (j.contains("audioFormat")) m_audioFormat = j["audioFormat"];
    if (j.contains("audioQuality")) m_audioQuality = j["audioQuality"];
    if (j.contains("embedThumbnail")) m_embedThumbnail = j["embedThumbnail"];
    if (j.contains("embedMetadata")) m_embedMetadata = j["embedMetadata"];
    if (j.contains("downloadSubtitles")) m_downloadSubtitles = j["downloadSubtitles"];
    if (j.contains("subtitleLanguage")) m_subtitleLanguage = j["subtitleLanguage"];
    if (j.contains("speedLimit")) m_speedLimit = j["speedLimit"];
    if (j.contains("theme")) m_theme = j["theme"];
    if (j.contains("autoQueue")) m_autoQueue = j["autoQueue"];
    if (j.contains("keepVideo")) m_keepVideo = j["keepVideo"];
}

std::string SettingsManager::GetSettingsPath()
{
#ifdef _WIN32
    char path[MAX_PATH];
    if (SHGetFolderPathA(NULL, CSIDL_APPDATA, NULL, 0, path) == S_OK)
    {
        std::string appDataPath = std::string(path) + "\\MyDownloader";
        FileUtils::CreateDirectory(appDataPath);
        return appDataPath + "\\settings.json";
    }
    return "settings.json";
#else
    const char* home = getenv("HOME");
    if (!home)
    {
        struct passwd* pw = getpwuid(getuid());
        home = pw->pw_dir;
    }
    std::string configPath = std::string(home) + "/.config/MyDownloader";
    FileUtils::CreateDirectory(configPath);
    return configPath + "/settings.json";
#endif
}
