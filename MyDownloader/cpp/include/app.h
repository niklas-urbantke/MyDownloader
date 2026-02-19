#pragma once

#include <wx/wx.h>

class MainFrame;

/**
 * MyDownloader Application Class
 * Cross-platform with native UI elements
 */
class MyDownloaderApp : public wxApp
{
public:
    virtual bool OnInit() override;
    virtual int OnExit() override;

private:
    MainFrame* m_mainFrame;
};

wxDECLARE_APP(MyDownloaderApp);
