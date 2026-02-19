#include "ui/settings_panel.h"
#include "core/settings_manager.h"
#include <wx/sizer.h>
#include <wx/statbox.h>

wxBEGIN_EVENT_TABLE(SettingsPanel, wxPanel)
wxEND_EVENT_TABLE()

SettingsPanel::SettingsPanel(wxWindow* parent)
    : wxPanel(parent),
      m_settingsManager(std::make_shared<SettingsManager>())
{
    CreateControls();
    LayoutControls();
    LoadSettings();
}

SettingsPanel::~SettingsPanel()
{
}

void SettingsPanel::CreateControls()
{
    m_downloadFolderPicker = new wxDirPickerCtrl(this, wxID_ANY);
    
    wxArrayString formats;
    formats.Add("mp3"); formats.Add("m4a"); formats.Add("opus"); formats.Add("flac"); formats.Add("wav");
    m_audioFormatCombo = new wxComboBox(this, wxID_ANY, "mp3", wxDefaultPosition, wxDefaultSize, formats, wxCB_READONLY);
    
    wxArrayString qualities;
    for (int i = 0; i <= 9; i++) qualities.Add(wxString::Format("%d", i));
    m_audioQualityCombo = new wxComboBox(this, wxID_ANY, "0", wxDefaultPosition, wxDefaultSize, qualities, wxCB_READONLY);
    
    m_embedThumbnailCheck = new wxCheckBox(this, wxID_ANY, "Embed Thumbnail");
    m_embedMetadataCheck = new wxCheckBox(this, wxID_ANY, "Embed Metadata");
    m_downloadSubtitlesCheck = new wxCheckBox(this, wxID_ANY, "Download Subtitles");
    m_autoQueueCheck = new wxCheckBox(this, wxID_ANY, "Auto Queue");
    
    m_subtitleLanguageText = new wxTextCtrl(this, wxID_ANY, "de,en");
    m_speedLimitSpin = new wxSpinCtrl(this, wxID_ANY);
    m_speedLimitSpin->SetRange(0, 10000);
    
    wxArrayString themes;
    themes.Add("System"); themes.Add("Light"); themes.Add("Dark");
    m_themeRadio = new wxRadioBox(this, wxID_ANY, "Theme", wxDefaultPosition, wxDefaultSize, themes);
    
    m_saveButton = new wxButton(this, wxID_ANY, "💾 Save Settings");
    m_resetButton = new wxButton(this, wxID_ANY, "🔄 Reset to Defaults");
    m_openFolderButton = new wxButton(this, wxID_ANY, "📁 Open Download Folder");
}

void SettingsPanel::LayoutControls()
{
    wxBoxSizer* mainSizer = new wxBoxSizer(wxVERTICAL);
    
    // Download folder
    wxStaticBoxSizer* folderBox = new wxStaticBoxSizer(wxVERTICAL, this, "Download Location");
    folderBox->Add(m_downloadFolderPicker, 0, wxEXPAND | wxALL, 5);
    folderBox->Add(m_openFolderButton, 0, wxALL, 5);
    mainSizer->Add(folderBox, 0, wxEXPAND | wxALL, 10);
    
    // Audio settings
    wxStaticBoxSizer* audioBox = new wxStaticBoxSizer(wxVERTICAL, this, "Audio Settings");
    wxBoxSizer* formatSizer = new wxBoxSizer(wxHORIZONTAL);
    formatSizer->Add(new wxStaticText(this, wxID_ANY, "Format:"), 0, wxALIGN_CENTER_VERTICAL | wxRIGHT, 5);
    formatSizer->Add(m_audioFormatCombo, 1, wxRIGHT, 10);
    formatSizer->Add(new wxStaticText(this, wxID_ANY, "Quality:"), 0, wxALIGN_CENTER_VERTICAL | wxRIGHT, 5);
    formatSizer->Add(m_audioQualityCombo, 1);
    audioBox->Add(formatSizer, 0, wxEXPAND | wxALL, 5);
    audioBox->Add(m_embedThumbnailCheck, 0, wxALL, 5);
    audioBox->Add(m_embedMetadataCheck, 0, wxALL, 5);
    mainSizer->Add(audioBox, 0, wxEXPAND | wxLEFT | wxRIGHT | wxBOTTOM, 10);
    
    // Theme
    mainSizer->Add(m_themeRadio, 0, wxEXPAND | wxLEFT | wxRIGHT | wxBOTTOM, 10);
    
    // Buttons
    wxBoxSizer* buttonSizer = new wxBoxSizer(wxHORIZONTAL);
    buttonSizer->Add(m_saveButton, 0, wxRIGHT, 5);
    buttonSizer->Add(m_resetButton, 0);
    mainSizer->Add(buttonSizer, 0, wxALL, 10);
    
    SetSizer(mainSizer);
}

void SettingsPanel::LoadSettings()
{
    m_settingsManager->Load();
    m_downloadFolderPicker->SetPath(wxString::FromUTF8(m_settingsManager->GetDownloadFolder()));
    m_audioFormatCombo->SetValue(wxString::FromUTF8(m_settingsManager->GetAudioFormat()));
    m_audioQualityCombo->SetSelection(m_settingsManager->GetAudioQuality());
    m_embedThumbnailCheck->SetValue(m_settingsManager->GetEmbedThumbnail());
    m_embedMetadataCheck->SetValue(m_settingsManager->GetEmbedMetadata());
}

void SettingsPanel::SaveSettings()
{
    m_settingsManager->SetDownloadFolder(m_downloadFolderPicker->GetPath().ToStdString());
    m_settingsManager->SetAudioFormat(m_audioFormatCombo->GetValue().ToStdString());
    m_settingsManager->SetAudioQuality(m_audioQualityCombo->GetSelection());
    m_settingsManager->SetEmbedThumbnail(m_embedThumbnailCheck->GetValue());
    m_settingsManager->SetEmbedMetadata(m_embedMetadataCheck->GetValue());
    m_settingsManager->Save();
    
    wxMessageBox("Settings saved successfully!", "Success", wxOK | wxICON_INFORMATION);
}

void SettingsPanel::OnSave(wxCommandEvent& event) { SaveSettings(); }
void SettingsPanel::OnReset(wxCommandEvent& event) { }
void SettingsPanel::OnOpenFolder(wxCommandEvent& event) { }
void SettingsPanel::OnThemeChange(wxCommandEvent& event) { }
void SettingsPanel::ApplyTheme(const wxString& theme) { }
