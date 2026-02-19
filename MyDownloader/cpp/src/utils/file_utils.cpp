#include "utils/file_utils.h"
#include <fstream>
#include <sstream>
#include <sys/stat.h>
#include <regex>

#ifdef _WIN32
#include <windows.h>
#include <direct.h>
#define mkdir _mkdir
#define stat _stat
#else
#include <unistd.h>
#include <dirent.h>
#include <libgen.h>
#endif

namespace FileUtils
{
    std::string GetExecutablePath()
    {
#ifdef _WIN32
        char path[MAX_PATH];
        GetModuleFileNameA(NULL, path, MAX_PATH);
        return std::string(path);
#else
        char path[1024];
        ssize_t len = readlink("/proc/self/exe", path, sizeof(path) - 1);
        if (len != -1)
        {
            path[len] = '\0';
            return std::string(path);
        }
        return "";
#endif
    }

    std::string GetConfigPath()
    {
#ifdef _WIN32
        char path[MAX_PATH];
        if (SHGetFolderPathA(NULL, CSIDL_APPDATA, NULL, 0, path) == S_OK)
        {
            return std::string(path) + "\\MyDownloader";
        }
        return ".";
#else
        const char* home = getenv("HOME");
        if (home)
        {
            return std::string(home) + "/.config/MyDownloader";
        }
        return ".";
#endif
    }

    std::string GetDataPath()
    {
        return GetConfigPath();
    }

    std::string JoinPath(const std::string& path1, const std::string& path2)
    {
#ifdef _WIN32
        char sep = '\\';
#else
        char sep = '/';
#endif
        if (path1.empty()) return path2;
        if (path2.empty()) return path1;
        
        if (path1.back() == sep)
            return path1 + path2;
        else
            return path1 + sep + path2;
    }

    std::string GetFileExtension(const std::string& filename)
    {
        size_t pos = filename.find_last_of('.');
        if (pos != std::string::npos)
            return filename.substr(pos + 1);
        return "";
    }

    std::string GetFileName(const std::string& path)
    {
#ifdef _WIN32
        size_t pos = path.find_last_of("\\/");
#else
        size_t pos = path.find_last_of('/');
#endif
        if (pos != std::string::npos)
            return path.substr(pos + 1);
        return path;
    }

    std::string GetBaseName(const std::string& path)
    {
        std::string filename = GetFileName(path);
        size_t pos = filename.find_last_of('.');
        if (pos != std::string::npos)
            return filename.substr(0, pos);
        return filename;
    }

    std::string GetDirectory(const std::string& path)
    {
#ifdef _WIN32
        size_t pos = path.find_last_of("\\/");
#else
        size_t pos = path.find_last_of('/');
#endif
        if (pos != std::string::npos)
            return path.substr(0, pos);
        return ".";
    }

    bool FileExists(const std::string& path)
    {
        struct stat buffer;
        return (stat(path.c_str(), &buffer) == 0 && !(buffer.st_mode & S_IFDIR));
    }

    bool DirectoryExists(const std::string& path)
    {
        struct stat buffer;
        return (stat(path.c_str(), &buffer) == 0 && (buffer.st_mode & S_IFDIR));
    }

    bool CreateDirectory(const std::string& path)
    {
#ifdef _WIN32
        return _mkdir(path.c_str()) == 0 || errno == EEXIST;
#else
        return mkdir(path.c_str(), 0755) == 0 || errno == EEXIST;
#endif
    }

    bool DeleteFile(const std::string& path)
    {
        return remove(path.c_str()) == 0;
    }

    bool CopyFile(const std::string& src, const std::string& dest)
    {
        std::ifstream srcFile(src, std::ios::binary);
        std::ofstream destFile(dest, std::ios::binary);
        
        if (!srcFile || !destFile)
            return false;
        
        destFile << srcFile.rdbuf();
        return true;
    }

    bool MoveFile(const std::string& src, const std::string& dest)
    {
        return rename(src.c_str(), dest.c_str()) == 0;
    }

    std::string ReadFile(const std::string& path)
    {
        std::ifstream file(path);
        if (!file.is_open())
            return "";
        
        std::stringstream buffer;
        buffer << file.rdbuf();
        return buffer.str();
    }

    bool WriteFile(const std::string& path, const std::string& content)
    {
        // Create directory if it doesn't exist
        std::string dir = GetDirectory(path);
        if (!DirectoryExists(dir))
        {
            CreateDirectory(dir);
        }
        
        std::ofstream file(path);
        if (!file.is_open())
            return false;
        
        file << content;
        return true;
    }

    std::vector<std::string> ReadLines(const std::string& path)
    {
        std::vector<std::string> lines;
        std::ifstream file(path);
        if (!file.is_open())
            return lines;
        
        std::string line;
        while (std::getline(file, line))
        {
            lines.push_back(line);
        }
        
        return lines;
    }

    size_t GetFileSize(const std::string& path)
    {
        struct stat buffer;
        if (stat(path.c_str(), &buffer) == 0)
            return buffer.st_size;
        return 0;
    }

    std::string FormatFileSize(size_t bytes)
    {
        const char* units[] = { "B", "KB", "MB", "GB", "TB" };
        int unit = 0;
        double size = static_cast<double>(bytes);
        
        while (size >= 1024.0 && unit < 4)
        {
            size /= 1024.0;
            unit++;
        }
        
        char buffer[64];
        snprintf(buffer, sizeof(buffer), "%.2f %s", size, units[unit]);
        return std::string(buffer);
    }

    std::string SanitizeFileName(const std::string& filename)
    {
        std::string result = filename;
        
        // Remove/replace invalid characters
        std::regex invalidChars(R"([<>:"/\\|?*])");
        result = std::regex_replace(result, invalidChars, "_");
        
        // Remove leading/trailing spaces and dots
        size_t start = result.find_first_not_of(" .");
        size_t end = result.find_last_not_of(" .");
        
        if (start != std::string::npos && end != std::string::npos)
            result = result.substr(start, end - start + 1);
        
        return result;
    }
}
