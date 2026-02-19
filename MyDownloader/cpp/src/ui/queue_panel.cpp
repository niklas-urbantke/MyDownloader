#include "ui/queue_panel.h"
#include "core/queue_manager.h"
#include <wx/sizer.h>

wxBEGIN_EVENT_TABLE(QueuePanel, wxPanel)
wxEND_EVENT_TABLE()

QueuePanel::QueuePanel(wxWindow* parent)
    : wxPanel(parent),
      m_queueManager(std::make_shared<QueueManager>())
{
    CreateControls();
    LayoutControls();
}

QueuePanel::~QueuePanel()
{
}

void QueuePanel::CreateControls()
{
    // List control
    m_queueList = new wxListCtrl(this, wxID_ANY, wxDefaultPosition, wxDefaultSize, 
                                  wxLC_REPORT | wxLC_SINGLE_SEL);
    m_queueList->AppendColumn("Status", wxLIST_FORMAT_LEFT, 80);
    m_queueList->AppendColumn("Title", wxLIST_FORMAT_LEFT, 400);
    m_queueList->AppendColumn("Format", wxLIST_FORMAT_LEFT, 80);
    m_queueList->AppendColumn("Progress", wxLIST_FORMAT_LEFT, 100);
    
    // Buttons
    m_startQueueButton = new wxButton(this, wxID_ANY, "▶️ Start Queue");
    m_pauseQueueButton = new wxButton(this, wxID_ANY, "⏸️ Pause");
    m_clearQueueButton = new wxButton(this, wxID_ANY, "🗑️ Clear");
    m_removeSelectedButton = new wxButton(this, wxID_ANY, "➖ Remove");
    m_moveUpButton = new wxButton(this, wxID_ANY, "⬆️ Move Up");
    m_moveDownButton = new wxButton(this, wxID_ANY, "⬇️ Move Down");
    
    // Status
    m_queueStatusLabel = new wxStaticText(this, wxID_ANY, "Queue: 0 items");
    m_overallProgressBar = new wxGauge(this, wxID_ANY, 100);
}

void QueuePanel::LayoutControls()
{
    wxBoxSizer* mainSizer = new wxBoxSizer(wxVERTICAL);
    
    mainSizer->Add(m_queueStatusLabel, 0, wxALL, 10);
    mainSizer->Add(m_queueList, 1, wxEXPAND | wxLEFT | wxRIGHT | wxBOTTOM, 10);
    
    wxBoxSizer* buttonSizer = new wxBoxSizer(wxHORIZONTAL);
    buttonSizer->Add(m_startQueueButton, 0, wxRIGHT, 5);
    buttonSizer->Add(m_pauseQueueButton, 0, wxRIGHT, 5);
    buttonSizer->Add(m_clearQueueButton, 0, wxRIGHT, 5);
    buttonSizer->Add(m_removeSelectedButton, 0, wxRIGHT, 5);
    buttonSizer->Add(m_moveUpButton, 0, wxRIGHT, 5);
    buttonSizer->Add(m_moveDownButton, 0);
    
    mainSizer->Add(buttonSizer, 0, wxLEFT | wxRIGHT | wxBOTTOM, 10);
    mainSizer->Add(m_overallProgressBar, 0, wxEXPAND | wxLEFT | wxRIGHT | wxBOTTOM, 10);
    
    SetSizer(mainSizer);
}

void QueuePanel::AddToQueue(const wxString& url, const wxString& format, int quality)
{
    // TODO: Implement
}

void QueuePanel::RefreshQueue()
{
    // TODO: Implement
}

void QueuePanel::OnStartQueue(wxCommandEvent& event) { }
void QueuePanel::OnPauseQueue(wxCommandEvent& event) { }
void QueuePanel::OnClearQueue(wxCommandEvent& event) { }
void QueuePanel::OnRemoveSelected(wxCommandEvent& event) { }
void QueuePanel::OnMoveUp(wxCommandEvent& event) { }
void QueuePanel::OnMoveDown(wxCommandEvent& event) { }
void QueuePanel::OnItemSelected(wxListEvent& event) { }
void QueuePanel::OnItemRightClick(wxListEvent& event) { }
void QueuePanel::UpdateQueueStatus() { }
int QueuePanel::GetSelectedItemIndex() { return -1; }
