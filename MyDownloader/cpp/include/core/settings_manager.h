#pragma once

#include <string>
#include <map>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

/**
 * Settings Manager - Manages application settings
 */
class SettingsManager
{
public:
    SettingsManager();
    ~SettingsManager();

    // Load/Save
    void Load();
    void Save();
    void Reset();
    
    // Getters
    std::string GetDownloadFolder() const { return m_downloadFolder; }
    std::string GetAudioFormat() const { return m_audioFormat; }
    int GetAudioQuality() const { return m_audioQuality; }
    bool GetEmbedThumbnail() const { return m_embedThumbnail; }
    bool GetEmbedMetadata() const { return m_embedMetadata; }
    bool GetDownloadSubtitles() const { return m_downloadSubtitles; }
    std::string GetSubtitleLanguage() const { return m_subtitleLanguage; }
    int GetSpeedLimit() const { return m_speedLimit; }
    std::string GetTheme() const { return m_theme; }
    bool GetAutoQueue() const { return m_autoQueue; }
    bool GetKeepVideo() const { return m_keepVideo; }
    
    // Setters
    void SetDownloadFolder(const std::string& folder) { m_downloadFolder = folder; }
    void SetAudioFormat(const std::string& format) { m_audioFormat = format; }
    void SetAudioQuality(int quality) { m_audioQuality = quality; }
    void SetEmbedThumbnail(bool embed) { m_embedThumbnail = embed; }
    void SetEmbedMetadata(bool embed) { m_embedMetadata = embed; }
    void SetDownloadSubtitles(bool download) { m_downloadSubtitles = download; }
    void SetSubtitleLanguage(const std::string& lang) { m_subtitleLanguage = lang; }
    void SetSpeedLimit(int limit) { m_speedLimit = limit; }
    void SetTheme(const std::string& theme) { m_theme = theme; }
    void SetAutoQueue(bool autoQueue) { m_autoQueue = autoQueue; }
    void SetKeepVideo(bool keep) { m_keepVideo = keep; }
    
    // Get default settings path
    static std::string GetSettingsPath();

private:
    std::string m_downloadFolder;
    std::string m_audioFormat;
    int m_audioQuality;
    bool m_embedThumbnail;
    bool m_embedMetadata;
    bool m_downloadSubtitles;
    std::string m_subtitleLanguage;
    int m_speedLimit;
    std::string m_theme;
    bool m_autoQueue;
    bool m_keepVideo;
    
    std::string m_settingsPath;
    
    void LoadDefaults();
    json ToJson() const;
    void FromJson(const json& j);
};
