#include "ui/history_panel.h"
#include "core/history_manager.h"
#include <wx/sizer.h>
#include <wx/srchctrl.h>

wxBEGIN_EVENT_TABLE(HistoryPanel, wxPanel)
wxEND_EVENT_TABLE()

HistoryPanel::HistoryPanel(wxWindow* parent)
    : wxPanel(parent),
      m_historyManager(std::make_shared<HistoryManager>())
{
    CreateControls();
    LayoutControls();
    m_historyManager->Load();
    RefreshHistory();
}

HistoryPanel::~HistoryPanel()
{
}

void HistoryPanel::CreateControls()
{
    m_searchCtrl = new wxSearchCtrl(this, wxID_ANY);
    
    m_historyList = new wxListCtrl(this, wxID_ANY, wxDefaultPosition, wxDefaultSize, 
                                    wxLC_REPORT | wxLC_SINGLE_SEL);
    m_historyList->AppendColumn("Date", wxLIST_FORMAT_LEFT, 150);
    m_historyList->AppendColumn("Title", wxLIST_FORMAT_LEFT, 400);
    m_historyList->AppendColumn("Format", wxLIST_FORMAT_LEFT, 80);
    
    m_clearHistoryButton = new wxButton(this, wxID_ANY, "Clear History");
    m_exportHistoryButton = new wxButton(this, wxID_ANY, "Export");
    m_redownloadButton = new wxButton(this, wxID_ANY, "Redownload");
    
    m_totalDownloadsLabel = new wxStaticText(this, wxID_ANY, "Total downloads: 0");
}

void HistoryPanel::LayoutControls()
{
    wxBoxSizer* mainSizer = new wxBoxSizer(wxVERTICAL);
    
    mainSizer->Add(m_searchCtrl, 0, wxEXPAND | wxALL, 10);
    mainSizer->Add(m_historyList, 1, wxEXPAND | wxLEFT | wxRIGHT | wxBOTTOM, 10);
    
    wxBoxSizer* buttonSizer = new wxBoxSizer(wxHORIZONTAL);
    buttonSizer->Add(m_clearHistoryButton, 0, wxRIGHT, 5);
    buttonSizer->Add(m_exportHistoryButton, 0, wxRIGHT, 5);
    buttonSizer->Add(m_redownloadButton, 0);
    
    mainSizer->Add(buttonSizer, 0, wxLEFT | wxRIGHT | wxBOTTOM, 10);
    mainSizer->Add(m_totalDownloadsLabel, 0, wxLEFT | wxRIGHT | wxBOTTOM, 10);
    
    SetSizer(mainSizer);
}

void HistoryPanel::RefreshHistory()
{
    m_historyList->DeleteAllItems();
    auto entries = m_historyManager->GetAllEntries();
    
    for (size_t i = 0; i < entries.size(); i++)
    {
        long index = m_historyList->InsertItem(i, wxString::FromUTF8(entries[i].timestamp));
        m_historyList->SetItem(index, 1, wxString::FromUTF8(entries[i].title));
        m_historyList->SetItem(index, 2, wxString::FromUTF8(entries[i].format));
    }
    
    m_totalDownloadsLabel->SetLabel(wxString::Format("Total downloads: %zu", entries.size()));
}

void HistoryPanel::AddHistoryEntry(const wxString& url, const wxString& title)
{
    m_historyManager->AddEntry(url.ToStdString(), title.ToStdString(), "mp3");
    RefreshHistory();
}

void HistoryPanel::OnClearHistory(wxCommandEvent& event) { }
void HistoryPanel::OnExportHistory(wxCommandEvent& event) { }
void HistoryPanel::OnRedownload(wxCommandEvent& event) { }
void HistoryPanel::OnSearch(wxCommandEvent& event) { }
void HistoryPanel::OnItemSelected(wxListEvent& event) { }
void HistoryPanel::OnItemActivated(wxListEvent& event) { }
void HistoryPanel::UpdateHistoryDisplay() { }
void HistoryPanel::FilterHistory(const wxString& searchTerm) { }
