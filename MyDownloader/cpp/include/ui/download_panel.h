#pragma once

#include <wx/wx.h>
#include <wx/gauge.h>
#include <wx/combobox.h>
#include <wx/textctrl.h>
#include <memory>

class Downloader;

/**
 * Download Panel - Main download interface
 */
class DownloadPanel : public wxPanel
{
public:
    DownloadPanel(wxWindow* parent);
    virtual ~DownloadPanel();

private:
    // UI Components
    wxTextCtrl* m_urlInput;
    wxButton* m_downloadButton;
    wxButton* m_pasteButton;
    wxButton* m_addToQueueButton;
    
    wxComboBox* m_formatCombo;
    wxComboBox* m_qualityCombo;
    wxCheckBox* m_playlistCheckbox;
    wxCheckBox* m_thumbnailCheckbox;
    wxCheckBox* m_metadataCheckbox;
    
    wxGauge* m_progressBar;
    wxStaticText* m_progressLabel;
    wxTextCtrl* m_logTextCtrl;
    
    wxButton* m_clearLogButton;
    
    // Downloader instance
    std::shared_ptr<Downloader> m_downloader;
    
    // Event Handlers
    void OnDownload(wxCommandEvent& event);
    void OnPaste(wxCommandEvent& event);
    void OnAddToQueue(wxCommandEvent& event);
    void OnClearLog(wxCommandEvent& event);
    void OnFormatChange(wxCommandEvent& event);
    
    // Helper Methods
    void CreateControls();
    void LayoutControls();
    void UpdateProgress(int percent, const wxString& status);
    void Log(const wxString& message);
    bool ValidateUrl(const wxString& url);
    
    wxDECLARE_EVENT_TABLE();
};

// Custom events
wxDECLARE_EVENT(wxEVT_DOWNLOAD_PROGRESS, wxCommandEvent);
wxDECLARE_EVENT(wxEVT_DOWNLOAD_COMPLETE, wxCommandEvent);
wxDECLARE_EVENT(wxEVT_DOWNLOAD_ERROR, wxCommandEvent);
