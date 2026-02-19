#include "ui/info_panel.h"
#include <wx/sizer.h>
#include <wx/stattext.h>

wxBEGIN_EVENT_TABLE(InfoPanel, wxPanel)
wxEND_EVENT_TABLE()

InfoPanel::InfoPanel(wxWindow* parent)
    : wxPanel(parent)
{
    CreateControls();
    LayoutControls();
    LoadApplicationInfo();
}

InfoPanel::~InfoPanel()
{
}

void InfoPanel::CreateControls()
{
    m_versionLabel = new wxStaticText(this, wxID_ANY, "MyDownloader v3.0", 
                                      wxDefaultPosition, wxDefaultSize, wxALIGN_CENTRE_HORIZONTAL);
    wxFont font = m_versionLabel->GetFont();
    font.PointSize(16);
    font.MakeBold();
    m_versionLabel->SetFont(font);
    
    m_descriptionLabel = new wxStaticText(this, wxID_ANY, 
        "Ultimate Music & Video Downloader\nwith native UI elements for each platform");
    
    m_githubLink = new wxHyperlinkCtrl(this, wxID_ANY, "GitHub Repository", 
                                       "https://github.com/");
    m_licenseLink = new wxHyperlinkCtrl(this, wxID_ANY, "MIT License", 
                                        "https://opensource.org/licenses/MIT");
    
    m_featuresText = new wxTextCtrl(this, wxID_ANY, "", wxDefaultPosition, wxSize(-1, 200), 
                                    wxTE_MULTILINE | wxTE_READONLY | wxTE_WORDWRAP);
    m_creditsText = new wxTextCtrl(this, wxID_ANY, "", wxDefaultPosition, wxSize(-1, 150), 
                                   wxTE_MULTILINE | wxTE_READONLY | wxTE_WORDWRAP);
    
    m_checkUpdatesButton = new wxButton(this, wxID_ANY, "🔍 Check for Updates");
    m_openDocsButton = new wxButton(this, wxID_ANY, "📖 Documentation");
}

void InfoPanel::LayoutControls()
{
    wxBoxSizer* mainSizer = new wxBoxSizer(wxVERTICAL);
    
    mainSizer->AddSpacer(20);
    mainSizer->Add(m_versionLabel, 0, wxEXPAND | wxLEFT | wxRIGHT, 20);
    mainSizer->AddSpacer(10);
    mainSizer->Add(m_descriptionLabel, 0, wxALIGN_CENTER | wxLEFT | wxRIGHT, 20);
    mainSizer->AddSpacer(20);
    
    wxBoxSizer* linkSizer = new wxBoxSizer(wxHORIZONTAL);
    linkSizer->Add(m_githubLink, 0, wxRIGHT, 20);
    linkSizer->Add(m_licenseLink, 0);
    mainSizer->Add(linkSizer, 0, wxALIGN_CENTER | wxLEFT | wxRIGHT, 20);
    
    mainSizer->AddSpacer(20);
    mainSizer->Add(new wxStaticText(this, wxID_ANY, "Features:"), 0, wxLEFT | wxRIGHT, 20);
    mainSizer->Add(m_featuresText, 0, wxEXPAND | wxLEFT | wxRIGHT | wxBOTTOM, 20);
    
    mainSizer->Add(new wxStaticText(this, wxID_ANY, "Credits:"), 0, wxLEFT | wxRIGHT, 20);
    mainSizer->Add(m_creditsText, 0, wxEXPAND | wxLEFT | wxRIGHT | wxBOTTOM, 20);
    
    wxBoxSizer* buttonSizer = new wxBoxSizer(wxHORIZONTAL);
    buttonSizer->Add(m_checkUpdatesButton, 0, wxRIGHT, 5);
    buttonSizer->Add(m_openDocsButton, 0);
    mainSizer->Add(buttonSizer, 0, wxALIGN_CENTER | wxALL, 20);
    
    SetSizer(mainSizer);
}

void InfoPanel::LoadApplicationInfo()
{
    m_featuresText->SetValue(
        "✅ Download from YouTube and other platforms\n"
        "✅ Multiple audio formats (MP3, M4A, OPUS, FLAC, WAV)\n"
        "✅ Quality settings (0-9)\n"
        "✅ Playlist support\n"
        "✅ Queue management\n"
        "✅ Download history\n"
        "✅ Thumbnail embedding\n"
        "✅ Metadata embedding\n"
        "✅ Native UI elements on Windows, macOS, and Linux"
    );
    
    m_creditsText->SetValue(
        "Built with:\n"
        "- wxWidgets for cross-platform native UI\n"
        "- yt-dlp for downloading\n"
        "- FFmpeg for audio conversion\n"
        "- nlohmann/json for JSON parsing\n\n"
        "© 2026 Urbantke Service Technics"
    );
}

void InfoPanel::OnCheckUpdates(wxCommandEvent& event) { }
void InfoPanel::OnOpenDocs(wxCommandEvent& event) { }
