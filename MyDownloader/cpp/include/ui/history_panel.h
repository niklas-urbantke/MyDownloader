#pragma once

#include <wx/wx.h>
#include <wx/listctrl.h>
#include <memory>

class HistoryManager;

/**
 * History Panel - Show download history
 */
class HistoryPanel : public wxPanel
{
public:
    HistoryPanel(wxWindow* parent);
    virtual ~HistoryPanel();

    void RefreshHistory();
    void AddHistoryEntry(const wxString& url, const wxString& title);

private:
    // UI Components
    wxListCtrl* m_historyList;
    wxButton* m_clearHistoryButton;
    wxButton* m_exportHistoryButton;
    wxButton* m_redownloadButton;
    wxSearchCtrl* m_searchCtrl;
    
    wxStaticText* m_totalDownloadsLabel;
    
    // History manager
    std::shared_ptr<HistoryManager> m_historyManager;
    
    // Event Handlers
    void OnClearHistory(wxCommandEvent& event);
    void OnExportHistory(wxCommandEvent& event);
    void OnRedownload(wxCommandEvent& event);
    void OnSearch(wxCommandEvent& event);
    void OnItemSelected(wxListEvent& event);
    void OnItemActivated(wxListEvent& event);
    
    // Helper Methods
    void CreateControls();
    void LayoutControls();
    void UpdateHistoryDisplay();
    void FilterHistory(const wxString& searchTerm);
    
    wxDECLARE_EVENT_TABLE();
};
