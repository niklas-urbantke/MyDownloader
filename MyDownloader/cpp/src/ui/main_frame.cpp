#include "ui/main_frame.h"
#include "ui/download_panel.h"
#include "ui/queue_panel.h"
#include "ui/history_panel.h"
#include "ui/settings_panel.h"
#include "ui/info_panel.h"
#include <wx/artprov.h>

wxBEGIN_EVENT_TABLE(MainFrame, wxFrame)
    EVT_MENU(ID_Quit, MainFrame::OnQuit)
    EVT_MENU(ID_About, MainFrame::OnAbout)
    EVT_MENU(ID_Settings, MainFrame::OnSettings)
    EVT_CLOSE(MainFrame::OnClose)
wxEND_EVENT_TABLE()

MainFrame::MainFrame(const wxString& title)
    : wxFrame(nullptr, wxID_ANY, title, wxDefaultPosition, wxSize(1000, 700)),
      m_notebook(nullptr),
      m_statusBar(nullptr),
      m_downloadPanel(nullptr),
      m_queuePanel(nullptr),
      m_historyPanel(nullptr),
      m_settingsPanel(nullptr),
      m_infoPanel(nullptr)
{
    // Set window icon
    #ifdef __WXMSW__
    SetIcon(wxIcon("IDI_ICON1"));
    #endif
    
    // Create UI
    CreateMenuBar();
    CreateNotebook();
    CreateStatusBar_();
    
    // Center on screen
    Centre();
}

MainFrame::~MainFrame()
{
}

void MainFrame::CreateMenuBar()
{
    m_menuBar = new wxMenuBar();
    
    // File menu
    m_fileMenu = new wxMenu();
    m_fileMenu->Append(ID_Settings, "&Settings\tCtrl-,", "Open settings");
    m_fileMenu->AppendSeparator();
    m_fileMenu->Append(ID_Quit, "E&xit\tAlt-F4", "Quit this program");
    m_menuBar->Append(m_fileMenu, "&File");
    
    // Help menu
    m_helpMenu = new wxMenu();
    m_helpMenu->Append(ID_About, "&About\tF1", "Show about dialog");
    m_menuBar->Append(m_helpMenu, "&Help");
    
    SetMenuBar(m_menuBar);
}

void MainFrame::CreateNotebook()
{
    m_notebook = new wxNotebook(this, wxID_ANY);
    
    // Create panels
    m_downloadPanel = new DownloadPanel(m_notebook);
    m_queuePanel = new QueuePanel(m_notebook);
    m_historyPanel = new HistoryPanel(m_notebook);
    m_settingsPanel = new SettingsPanel(m_notebook);
    m_infoPanel = new InfoPanel(m_notebook);
    
    // Add pages to notebook
    m_notebook->AddPage(m_downloadPanel, "📥 Download", true);
    m_notebook->AddPage(m_queuePanel, "📋 Queue");
    m_notebook->AddPage(m_historyPanel, "📜 History");
    m_notebook->AddPage(m_settingsPanel, "⚙️ Settings");
    m_notebook->AddPage(m_infoPanel, "ℹ️ Info");
}

void MainFrame::CreateStatusBar_()
{
    m_statusBar = CreateStatusBar(2);
    SetStatusText("Ready", 0);
    SetStatusText("MyDownloader v3.0", 1);
}

void MainFrame::OnQuit(wxCommandEvent& WXUNUSED(event))
{
    Close(true);
}

void MainFrame::OnAbout(wxCommandEvent& WXUNUSED(event))
{
    wxMessageBox(
        "MyDownloader v3.0\n\n"
        "Ultimate Music & Video Downloader\n"
        "with native UI elements for each platform\n\n"
        "Built with wxWidgets and C++\n\n"
        "© 2026 Urbantke Service Technics",
        "About MyDownloader",
        wxOK | wxICON_INFORMATION,
        this
    );
}

void MainFrame::OnSettings(wxCommandEvent& WXUNUSED(event))
{
    // Switch to settings tab
    m_notebook->SetSelection(3);
}

void MainFrame::OnClose(wxCloseEvent& event)
{
    // Save settings before closing
    if (m_settingsPanel)
    {
        m_settingsPanel->SaveSettings();
    }
    
    event.Skip();
}
