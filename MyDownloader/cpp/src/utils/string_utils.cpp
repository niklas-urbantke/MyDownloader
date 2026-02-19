#include "utils/string_utils.h"
#include <algorithm>
#include <cctype>
#include <sstream>
#include <regex>

namespace StringUtils
{
    std::string ToLower(const std::string& str)
    {
        std::string result = str;
        std::transform(result.begin(), result.end(), result.begin(), ::tolower);
        return result;
    }

    std::string ToUpper(const std::string& str)
    {
        std::string result = str;
        std::transform(result.begin(), result.end(), result.begin(), ::toupper);
        return result;
    }

    std::string Trim(const std::string& str)
    {
        return TrimRight(TrimLeft(str));
    }

    std::string TrimLeft(const std::string& str)
    {
        size_t start = str.find_first_not_of(" \t\n\r");
        return (start == std::string::npos) ? "" : str.substr(start);
    }

    std::string TrimRight(const std::string& str)
    {
        size_t end = str.find_last_not_of(" \t\n\r");
        return (end == std::string::npos) ? "" : str.substr(0, end + 1);
    }

    std::vector<std::string> Split(const std::string& str, char delimiter)
    {
        std::vector<std::string> tokens;
        std::stringstream ss(str);
        std::string token;
        
        while (std::getline(ss, token, delimiter))
        {
            tokens.push_back(token);
        }
        
        return tokens;
    }

    std::vector<std::string> Split(const std::string& str, const std::string& delimiter)
    {
        std::vector<std::string> tokens;
        size_t start = 0;
        size_t end = str.find(delimiter);
        
        while (end != std::string::npos)
        {
            tokens.push_back(str.substr(start, end - start));
            start = end + delimiter.length();
            end = str.find(delimiter, start);
        }
        
        tokens.push_back(str.substr(start));
        return tokens;
    }

    std::string Join(const std::vector<std::string>& parts, const std::string& delimiter)
    {
        std::string result;
        for (size_t i = 0; i < parts.size(); i++)
        {
            result += parts[i];
            if (i < parts.size() - 1)
                result += delimiter;
        }
        return result;
    }

    bool StartsWith(const std::string& str, const std::string& prefix)
    {
        return str.size() >= prefix.size() && 
               str.compare(0, prefix.size(), prefix) == 0;
    }

    bool EndsWith(const std::string& str, const std::string& suffix)
    {
        return str.size() >= suffix.size() && 
               str.compare(str.size() - suffix.size(), suffix.size(), suffix) == 0;
    }

    bool Contains(const std::string& str, const std::string& substring)
    {
        return str.find(substring) != std::string::npos;
    }

    std::string Replace(const std::string& str, const std::string& from, const std::string& to)
    {
        std::string result = str;
        size_t pos = result.find(from);
        if (pos != std::string::npos)
        {
            result.replace(pos, from.length(), to);
        }
        return result;
    }

    std::string ReplaceAll(const std::string& str, const std::string& from, const std::string& to)
    {
        std::string result = str;
        size_t pos = 0;
        while ((pos = result.find(from, pos)) != std::string::npos)
        {
            result.replace(pos, from.length(), to);
            pos += to.length();
        }
        return result;
    }

    bool IsValidUrl(const std::string& url)
    {
        std::regex urlRegex(R"(^https?://[^\s/$.?#].[^\s]*$)", std::regex_constants::icase);
        return std::regex_match(url, urlRegex);
    }

    bool IsYouTubeUrl(const std::string& url)
    {
        return Contains(ToLower(url), "youtube.com") || 
               Contains(ToLower(url), "youtu.be");
    }

    bool IsPlaylistUrl(const std::string& url)
    {
        return Contains(url, "list=");
    }

    std::string ExtractVideoId(const std::string& url)
    {
        // Extract YouTube video ID from URL
        std::regex videoIdRegex(R"((?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11}))");
        std::smatch match;
        
        if (std::regex_search(url, match, videoIdRegex) && match.size() > 1)
        {
            return match[1].str();
        }
        
        return "";
    }

    std::string UrlEncode(const std::string& str)
    {
        std::ostringstream escaped;
        escaped.fill('0');
        escaped << std::hex;
        
        for (char c : str)
        {
            if (isalnum(c) || c == '-' || c == '_' || c == '.' || c == '~')
            {
                escaped << c;
            }
            else
            {
                escaped << '%' << std::setw(2) << int((unsigned char)c);
            }
        }
        
        return escaped.str();
    }

    std::string UrlDecode(const std::string& str)
    {
        std::string result;
        for (size_t i = 0; i < str.length(); i++)
        {
            if (str[i] == '%' && i + 2 < str.length())
            {
                int value;
                std::istringstream(str.substr(i + 1, 2)) >> std::hex >> value;
                result += static_cast<char>(value);
                i += 2;
            }
            else if (str[i] == '+')
            {
                result += ' ';
            }
            else
            {
                result += str[i];
            }
        }
        return result;
    }

    std::string FormatTime(int seconds)
    {
        int hours = seconds / 3600;
        int minutes = (seconds % 3600) / 60;
        int secs = seconds % 60;
        
        char buffer[16];
        if (hours > 0)
            snprintf(buffer, sizeof(buffer), "%d:%02d:%02d", hours, minutes, secs);
        else
            snprintf(buffer, sizeof(buffer), "%d:%02d", minutes, secs);
        
        return std::string(buffer);
    }

    std::string FormatBitrate(int bitrate)
    {
        if (bitrate >= 1000)
        {
            return std::to_string(bitrate / 1000) + " Mbps";
        }
        return std::to_string(bitrate) + " Kbps";
    }

    int ToInt(const std::string& str, int defaultValue)
    {
        try
        {
            return std::stoi(str);
        }
        catch (...)
        {
            return defaultValue;
        }
    }

    double ToDouble(const std::string& str, double defaultValue)
    {
        try
        {
            return std::stod(str);
        }
        catch (...)
        {
            return defaultValue;
        }
    }

    bool ToBool(const std::string& str)
    {
        std::string lower = ToLower(str);
        return lower == "true" || lower == "1" || lower == "yes" || lower == "on";
    }
}
