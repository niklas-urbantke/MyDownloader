#include "app.h"
#include "ui/main_frame.h"
#include "core/downloader.h"
#include <wx/stdpaths.h>

wxDEFINE_APP(MyDownloaderApp);

bool MyDownloaderApp::OnInit()
{
    // Set application name
    SetAppName("MyDownloader");
    SetVendorName("Urbantke Service Technics");
    
    // Initialize image handlers
    wxInitAllImageHandlers();
    
    // Check dependencies
    if (!Downloader::CheckYtDlpInstalled())
    {
        wxMessageBox(
            "yt-dlp is not installed or not found in PATH.\n"
            "Please install yt-dlp to use this application.\n\n"
            "Visit: https://github.com/yt-dlp/yt-dlp",
            "Missing Dependency",
            wxOK | wxICON_ERROR
        );
    }
    
    if (!Downloader::CheckFfmpegInstalled())
    {
        int result = wxMessageBox(
            "FFmpeg is not installed or not found in PATH.\n"
            "FFmpeg is required for audio conversion.\n\n"
            "Do you want to continue anyway?",
            "Missing Dependency",
            wxYES_NO | wxICON_WARNING
        );
        
        if (result == wxNO)
        {
            return false;
        }
    }
    
    // Create main frame
    m_mainFrame = new MainFrame("🎵 MyDownloader v3.0");
    m_mainFrame->Show(true);
    
    return true;
}

int MyDownloaderApp::OnExit()
{
    return wxApp::OnExit();
}
