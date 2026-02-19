#pragma once

#include <string>
#include <vector>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

/**
 * History entry
 */
struct HistoryEntry
{
    std::string url;
    std::string title;
    std::string timestamp;
    std::string format;
    bool success;
};

/**
 * History Manager - Manages download history
 */
class HistoryManager
{
public:
    HistoryManager();
    ~HistoryManager();

    // Load/Save
    void Load();
    void Save();
    void Clear();
    
    // Add entry
    void AddEntry(const std::string& url, const std::string& title, 
                  const std::string& format, bool success = true);
    
    // Get entries
    std::vector<HistoryEntry> GetAllEntries() const { return m_entries; }
    std::vector<HistoryEntry> SearchEntries(const std::string& query) const;
    int GetTotalDownloads() const { return static_cast<int>(m_entries.size()); }
    
    // Export
    void ExportToJson(const std::string& filename) const;
    void ExportToCsv(const std::string& filename) const;
    
    // Get default history path
    static std::string GetHistoryPath();

private:
    std::vector<HistoryEntry> m_entries;
    std::string m_historyPath;
    
    json ToJson() const;
    void FromJson(const json& j);
    std::string GetCurrentTimestamp() const;
};
