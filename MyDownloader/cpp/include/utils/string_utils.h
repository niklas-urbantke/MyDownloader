#pragma once

#include <string>
#include <vector>

/**
 * String utilities
 */
namespace StringUtils
{
    // Conversion
    std::string ToLower(const std::string& str);
    std::string ToUpper(const std::string& str);
    std::string Trim(const std::string& str);
    std::string TrimLeft(const std::string& str);
    std::string TrimRight(const std::string& str);
    
    // Splitting/Joining
    std::vector<std::string> Split(const std::string& str, char delimiter);
    std::vector<std::string> Split(const std::string& str, const std::string& delimiter);
    std::string Join(const std::vector<std::string>& parts, const std::string& delimiter);
    
    // Search/Replace
    bool StartsWith(const std::string& str, const std::string& prefix);
    bool EndsWith(const std::string& str, const std::string& suffix);
    bool Contains(const std::string& str, const std::string& substring);
    std::string Replace(const std::string& str, const std::string& from, const std::string& to);
    std::string ReplaceAll(const std::string& str, const std::string& from, const std::string& to);
    
    // URL utilities
    bool IsValidUrl(const std::string& url);
    bool IsYouTubeUrl(const std::string& url);
    bool IsPlaylistUrl(const std::string& url);
    std::string ExtractVideoId(const std::string& url);
    
    // Encoding
    std::string UrlEncode(const std::string& str);
    std::string UrlDecode(const std::string& str);
    
    // Format
    std::string FormatTime(int seconds);
    std::string FormatBitrate(int bitrate);
    
    // Conversion
    int ToInt(const std::string& str, int defaultValue = 0);
    double ToDouble(const std::string& str, double defaultValue = 0.0);
    bool ToBool(const std::string& str);
}
