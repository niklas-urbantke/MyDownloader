#pragma once

#include <wx/wx.h>
#include <wx/notebook.h>
#include <wx/statusbr.h>

class DownloadPanel;
class QueuePanel;
class HistoryPanel;
class SettingsPanel;
class InfoPanel;

/**
 * Main Application Frame with Tab-based Navigation
 */
class MainFrame : public wxFrame
{
public:
    MainFrame(const wxString& title);
    virtual ~MainFrame();

private:
    // UI Components
    wxNotebook* m_notebook;
    wxStatusBar* m_statusBar;
    
    // Panels (Tabs)
    DownloadPanel* m_downloadPanel;
    QueuePanel* m_queuePanel;
    HistoryPanel* m_historyPanel;
    SettingsPanel* m_settingsPanel;
    InfoPanel* m_infoPanel;
    
    // Menu
    wxMenuBar* m_menuBar;
    wxMenu* m_fileMenu;
    wxMenu* m_helpMenu;
    
    // Event Handlers
    void OnQuit(wxCommandEvent& event);
    void OnAbout(wxCommandEvent& event);
    void OnSettings(wxCommandEvent& event);
    void OnClose(wxCloseEvent& event);
    
    // Helper Methods
    void CreateMenuBar();
    void CreateNotebook();
    void CreateStatusBar_();
    
    wxDECLARE_EVENT_TABLE();
};

// Event IDs
enum
{
    ID_Quit = wxID_EXIT,
    ID_About = wxID_ABOUT,
    ID_Settings = wxID_PREFERENCES
};
