#include "core/history_manager.h"
#include "utils/file_utils.h"
#include <fstream>
#include <chrono>
#include <iomanip>
#include <sstream>

#ifdef _WIN32
#include <shlobj.h>
#include <windows.h>
#else
#include <unistd.h>
#include <pwd.h>
#endif

HistoryManager::HistoryManager()
{
    m_historyPath = GetHistoryPath();
}

HistoryManager::~HistoryManager()
{
}

void HistoryManager::Load()
{
    if (!FileUtils::FileExists(m_historyPath))
    {
        m_entries.clear();
        return;
    }
    
    try
    {
        std::string content = FileUtils::ReadFile(m_historyPath);
        json j = json::parse(content);
        FromJson(j);
    }
    catch (const std::exception& e)
    {
        m_entries.clear();
    }
}

void HistoryManager::Save()
{
    try
    {
        json j = ToJson();
        std::string content = j.dump(4);
        FileUtils::WriteFile(m_historyPath, content);
    }
    catch (const std::exception& e)
    {
        // Error saving
    }
}

void HistoryManager::Clear()
{
    m_entries.clear();
    Save();
}

void HistoryManager::AddEntry(const std::string& url, const std::string& title, 
                              const std::string& format, bool success)
{
    HistoryEntry entry;
    entry.url = url;
    entry.title = title;
    entry.timestamp = GetCurrentTimestamp();
    entry.format = format;
    entry.success = success;
    
    m_entries.push_back(entry);
    
    // Keep only last 100 entries
    if (m_entries.size() > 100)
    {
        m_entries.erase(m_entries.begin());
    }
    
    Save();
}

std::vector<HistoryEntry> HistoryManager::SearchEntries(const std::string& query) const
{
    std::vector<HistoryEntry> results;
    
    for (const auto& entry : m_entries)
    {
        if (entry.title.find(query) != std::string::npos ||
            entry.url.find(query) != std::string::npos)
        {
            results.push_back(entry);
        }
    }
    
    return results;
}

void HistoryManager::ExportToJson(const std::string& filename) const
{
    try
    {
        json j = ToJson();
        std::string content = j.dump(4);
        FileUtils::WriteFile(filename, content);
    }
    catch (const std::exception& e)
    {
        // Error exporting
    }
}

void HistoryManager::ExportToCsv(const std::string& filename) const
{
    std::ofstream file(filename);
    if (!file.is_open()) return;
    
    file << "Timestamp,Title,URL,Format,Success\n";
    
    for (const auto& entry : m_entries)
    {
        file << entry.timestamp << ","
             << "\"" << entry.title << "\","
             << entry.url << ","
             << entry.format << ","
             << (entry.success ? "Yes" : "No") << "\n";
    }
    
    file.close();
}

json HistoryManager::ToJson() const
{
    json j = json::array();
    
    for (const auto& entry : m_entries)
    {
        json item;
        item["url"] = entry.url;
        item["title"] = entry.title;
        item["timestamp"] = entry.timestamp;
        item["format"] = entry.format;
        item["success"] = entry.success;
        j.push_back(item);
    }
    
    return j;
}

void HistoryManager::FromJson(const json& j)
{
    m_entries.clear();
    
    if (!j.is_array()) return;
    
    for (const auto& item : j)
    {
        HistoryEntry entry;
        if (item.contains("url")) entry.url = item["url"];
        if (item.contains("title")) entry.title = item["title"];
        if (item.contains("timestamp")) entry.timestamp = item["timestamp"];
        if (item.contains("format")) entry.format = item["format"];
        if (item.contains("success")) entry.success = item["success"];
        
        m_entries.push_back(entry);
    }
}

std::string HistoryManager::GetCurrentTimestamp() const
{
    auto now = std::chrono::system_clock::now();
    auto time = std::chrono::system_clock::to_time_t(now);
    
    std::stringstream ss;
    ss << std::put_time(std::localtime(&time), "%Y-%m-%d %H:%M:%S");
    return ss.str();
}

std::string HistoryManager::GetHistoryPath()
{
#ifdef _WIN32
    char path[MAX_PATH];
    if (SHGetFolderPathA(NULL, CSIDL_APPDATA, NULL, 0, path) == S_OK)
    {
        std::string appDataPath = std::string(path) + "\\MyDownloader";
        FileUtils::CreateDirectory(appDataPath);
        return appDataPath + "\\history.json";
    }
    return "history.json";
#else
    const char* home = getenv("HOME");
    if (!home)
    {
        struct passwd* pw = getpwuid(getuid());
        home = pw->pw_dir;
    }
    std::string configPath = std::string(home) + "/.config/MyDownloader";
    FileUtils::CreateDirectory(configPath);
    return configPath + "/history.json";
#endif
}
