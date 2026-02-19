#include "ui/download_panel.h"
#include "core/downloader.h"
#include "utils/string_utils.h"
#include <wx/clipbrd.h>
#include <wx/sizer.h>

wxDEFINE_EVENT(wxEVT_DOWNLOAD_PROGRESS, wxCommandEvent);
wxDEFINE_EVENT(wxEVT_DOWNLOAD_COMPLETE, wxCommandEvent);
wxDEFINE_EVENT(wxEVT_DOWNLOAD_ERROR, wxCommandEvent);

wxBEGIN_EVENT_TABLE(DownloadPanel, wxPanel)
    EVT_BUTTON(wxID_ANY, DownloadPanel::OnDownload)
wxEND_EVENT_TABLE()

DownloadPanel::DownloadPanel(wxWindow* parent)
    : wxPanel(parent),
      m_downloader(std::make_shared<Downloader>())
{
    CreateControls();
    LayoutControls();
    
    // Setup callbacks
    m_downloader->SetProgressCallback([this](int percent, const std::string& status, const std::string& details) {
        UpdateProgress(percent, wxString::FromUTF8(status));
        Log(wxString::FromUTF8(details));
    });
    
    m_downloader->SetCompletionCallback([this](bool success, const std::string& message) {
        Log(wxString::FromUTF8(message));
        m_downloadButton->Enable(true);
    });
}

DownloadPanel::~DownloadPanel()
{
}

void DownloadPanel::CreateControls()
{
    // URL input
    wxStaticText* urlLabel = new wxStaticText(this, wxID_ANY, "URL:");
    m_urlInput = new wxTextCtrl(this, wxID_ANY, "", wxDefaultPosition, wxDefaultSize);
    m_pasteButton = new wxButton(this, wxID_ANY, "📋 Paste");
    
    // Buttons
    m_downloadButton = new wxButton(this, wxID_ANY, "⬇️ Download");
    m_addToQueueButton = new wxButton(this, wxID_ANY, "➕ Add to Queue");
    
    // Format selection
    wxStaticText* formatLabel = new wxStaticText(this, wxID_ANY, "Format:");
    wxArrayString formats;
    formats.Add("mp3");
    formats.Add("m4a");
    formats.Add("opus");
    formats.Add("flac");
    formats.Add("wav");
    m_formatCombo = new wxComboBox(this, wxID_ANY, "mp3", wxDefaultPosition, wxDefaultSize, formats, wxCB_READONLY);
    
    // Quality selection
    wxStaticText* qualityLabel = new wxStaticText(this, wxID_ANY, "Quality:");
    wxArrayString qualities;
    for (int i = 0; i <= 9; i++)
    {
        qualities.Add(wxString::Format("%d %s", i, i == 0 ? "(Best)" : i == 9 ? "(Smallest)" : ""));
    }
    m_qualityCombo = new wxComboBox(this, wxID_ANY, "0 (Best)", wxDefaultPosition, wxDefaultSize, qualities, wxCB_READONLY);
    
    // Checkboxes
    m_playlistCheckbox = new wxCheckBox(this, wxID_ANY, "Download as Playlist");
    m_thumbnailCheckbox = new wxCheckBox(this, wxID_ANY, "Embed Thumbnail");
    m_metadataCheckbox = new wxCheckBox(this, wxID_ANY, "Embed Metadata");
    
    m_thumbnailCheckbox->SetValue(true);
    m_metadataCheckbox->SetValue(true);
    
    // Progress
    m_progressLabel = new wxStaticText(this, wxID_ANY, "Ready");
    m_progressBar = new wxGauge(this, wxID_ANY, 100);
    
    // Log
    wxStaticText* logLabel = new wxStaticText(this, wxID_ANY, "Log:");
    m_logTextCtrl = new wxTextCtrl(this, wxID_ANY, "", wxDefaultPosition, wxSize(-1, 200), 
                                    wxTE_MULTILINE | wxTE_READONLY | wxTE_WORDWRAP);
    m_clearLogButton = new wxButton(this, wxID_ANY, "Clear Log");
}

void DownloadPanel::LayoutControls()
{
    wxBoxSizer* mainSizer = new wxBoxSizer(wxVERTICAL);
    
    // URL section
    wxBoxSizer* urlSizer = new wxBoxSizer(wxHORIZONTAL);
    urlSizer->Add(new wxStaticText(this, wxID_ANY, "URL:"), 0, wxALIGN_CENTER_VERTICAL | wxRIGHT, 5);
    urlSizer->Add(m_urlInput, 1, wxEXPAND | wxRIGHT, 5);
    urlSizer->Add(m_pasteButton, 0);
    mainSizer->Add(urlSizer, 0, wxEXPAND | wxALL, 10);
    
    // Format selection
    wxBoxSizer* formatSizer = new wxBoxSizer(wxHORIZONTAL);
    formatSizer->Add(new wxStaticText(this, wxID_ANY, "Format:"), 0, wxALIGN_CENTER_VERTICAL | wxRIGHT, 5);
    formatSizer->Add(m_formatCombo, 1, wxRIGHT, 10);
    formatSizer->Add(new wxStaticText(this, wxID_ANY, "Quality:"), 0, wxALIGN_CENTER_VERTICAL | wxRIGHT, 5);
    formatSizer->Add(m_qualityCombo, 1);
    mainSizer->Add(formatSizer, 0, wxEXPAND | wxLEFT | wxRIGHT | wxBOTTOM, 10);
    
    // Checkboxes
    mainSizer->Add(m_playlistCheckbox, 0, wxLEFT | wxRIGHT | wxBOTTOM, 10);
    mainSizer->Add(m_thumbnailCheckbox, 0, wxLEFT | wxRIGHT | wxBOTTOM, 10);
    mainSizer->Add(m_metadataCheckbox, 0, wxLEFT | wxRIGHT | wxBOTTOM, 10);
    
    // Buttons
    wxBoxSizer* buttonSizer = new wxBoxSizer(wxHORIZONTAL);
    buttonSizer->Add(m_downloadButton, 1, wxRIGHT, 5);
    buttonSizer->Add(m_addToQueueButton, 1);
    mainSizer->Add(buttonSizer, 0, wxEXPAND | wxLEFT | wxRIGHT | wxBOTTOM, 10);
    
    // Progress
    mainSizer->Add(m_progressLabel, 0, wxLEFT | wxRIGHT | wxBOTTOM, 10);
    mainSizer->Add(m_progressBar, 0, wxEXPAND | wxLEFT | wxRIGHT | wxBOTTOM, 10);
    
    // Log
    mainSizer->Add(new wxStaticText(this, wxID_ANY, "Log:"), 0, wxLEFT | wxRIGHT | wxBOTTOM, 10);
    mainSizer->Add(m_logTextCtrl, 1, wxEXPAND | wxLEFT | wxRIGHT | wxBOTTOM, 10);
    mainSizer->Add(m_clearLogButton, 0, wxLEFT | wxRIGHT | wxBOTTOM, 10);
    
    SetSizer(mainSizer);
}

void DownloadPanel::OnDownload(wxCommandEvent& event)
{
    wxString url = m_urlInput->GetValue();
    if (!ValidateUrl(url))
    {
        wxMessageBox("Please enter a valid URL", "Invalid URL", wxOK | wxICON_ERROR);
        return;
    }
    
    // Create config
    DownloadConfig config;
    config.url = url.ToStdString();
    config.format = m_formatCombo->GetValue().ToStdString();
    config.quality = m_qualityCombo->GetSelection();
    config.downloadPlaylist = m_playlistCheckbox->GetValue();
    config.embedThumbnail = m_thumbnailCheckbox->GetValue();
    config.embedMetadata = m_metadataCheckbox->GetValue();
    
    // Start download
    m_downloadButton->Enable(false);
    Log("Starting download...");
    m_downloader->Download(config);
}

void DownloadPanel::OnPaste(wxCommandEvent& event)
{
    if (wxTheClipboard->Open())
    {
        if (wxTheClipboard->IsSupported(wxDF_TEXT))
        {
            wxTextDataObject data;
            wxTheClipboard->GetData(data);
            m_urlInput->SetValue(data.GetText());
        }
        wxTheClipboard->Close();
    }
}

void DownloadPanel::OnAddToQueue(wxCommandEvent& event)
{
    // TODO: Implement
    wxMessageBox("Add to queue functionality coming soon!", "Info", wxOK | wxICON_INFORMATION);
}

void DownloadPanel::OnClearLog(wxCommandEvent& event)
{
    m_logTextCtrl->Clear();
}

void DownloadPanel::OnFormatChange(wxCommandEvent& event)
{
    // Update quality options based on format
}

void DownloadPanel::UpdateProgress(int percent, const wxString& status)
{
    m_progressBar->SetValue(percent);
    m_progressLabel->SetLabel(wxString::Format("%s (%d%%)", status, percent));
}

void DownloadPanel::Log(const wxString& message)
{
    m_logTextCtrl->AppendText(message + "\n");
}

bool DownloadPanel::ValidateUrl(const wxString& url)
{
    return StringUtils::IsValidUrl(url.ToStdString());
}
