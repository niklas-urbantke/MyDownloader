#pragma once

#include <wx/wx.h>
#include <wx/listctrl.h>
#include <memory>

class QueueManager;

/**
 * Queue Panel - Manage download queue
 */
class QueuePanel : public wxPanel
{
public:
    QueuePanel(wxWindow* parent);
    virtual ~QueuePanel();

    void AddToQueue(const wxString& url, const wxString& format, int quality);
    void RefreshQueue();

private:
    // UI Components
    wxListCtrl* m_queueList;
    wxButton* m_startQueueButton;
    wxButton* m_pauseQueueButton;
    wxButton* m_clearQueueButton;
    wxButton* m_removeSelectedButton;
    wxButton* m_moveUpButton;
    wxButton* m_moveDownButton;
    
    wxStaticText* m_queueStatusLabel;
    wxGauge* m_overallProgressBar;
    
    // Queue manager
    std::shared_ptr<QueueManager> m_queueManager;
    
    // Event Handlers
    void OnStartQueue(wxCommandEvent& event);
    void OnPauseQueue(wxCommandEvent& event);
    void OnClearQueue(wxCommandEvent& event);
    void OnRemoveSelected(wxCommandEvent& event);
    void OnMoveUp(wxCommandEvent& event);
    void OnMoveDown(wxCommandEvent& event);
    void OnItemSelected(wxListEvent& event);
    void OnItemRightClick(wxListEvent& event);
    
    // Helper Methods
    void CreateControls();
    void LayoutControls();
    void UpdateQueueStatus();
    int GetSelectedItemIndex();
    
    wxDECLARE_EVENT_TABLE();
};
