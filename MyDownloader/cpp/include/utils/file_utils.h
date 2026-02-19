#pragma once

#include <string>
#include <vector>

/**
 * File utilities
 */
namespace FileUtils
{
    // Path operations
    std::string GetExecutablePath();
    std::string GetConfigPath();
    std::string GetDataPath();
    std::string JoinPath(const std::string& path1, const std::string& path2);
    std::string GetFileExtension(const std::string& filename);
    std::string GetFileName(const std::string& path);
    std::string GetBaseName(const std::string& path);
    std::string GetDirectory(const std::string& path);
    
    // File operations
    bool FileExists(const std::string& path);
    bool DirectoryExists(const std::string& path);
    bool CreateDirectory(const std::string& path);
    bool DeleteFile(const std::string& path);
    bool CopyFile(const std::string& src, const std::string& dest);
    bool MoveFile(const std::string& src, const std::string& dest);
    
    // Read/Write
    std::string ReadFile(const std::string& path);
    bool WriteFile(const std::string& path, const std::string& content);
    std::vector<std::string> ReadLines(const std::string& path);
    
    // Size
    size_t GetFileSize(const std::string& path);
    std::string FormatFileSize(size_t bytes);
    
    // Cleanup
    std::string SanitizeFileName(const std::string& filename);
}
