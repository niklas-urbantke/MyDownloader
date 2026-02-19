#pragma once

#include <wx/wx.h>
#include <wx/filepicker.h>
#include <wx/spinctrl.h>
#include <memory>

class SettingsManager;

/**
 * Settings Panel - Application settings
 */
class SettingsPanel : public wxPanel
{
public:
    SettingsPanel(wxWindow* parent);
    virtual ~SettingsPanel();

    void LoadSettings();
    void SaveSettings();

private:
    // UI Components
    wxDirPickerCtrl* m_downloadFolderPicker;
    
    wxComboBox* m_audioFormatCombo;
    wxComboBox* m_audioQualityCombo;
    
    wxCheckBox* m_embedThumbnailCheck;
    wxCheckBox* m_embedMetadataCheck;
    wxCheckBox* m_downloadSubtitlesCheck;
    wxCheckBox* m_autoQueueCheck;
    
    wxTextCtrl* m_subtitleLanguageText;
    wxSpinCtrl* m_speedLimitSpin;
    
    wxRadioBox* m_themeRadio;
    
    wxButton* m_saveButton;
    wxButton* m_resetButton;
    wxButton* m_openFolderButton;
    
    // Settings manager
    std::shared_ptr<SettingsManager> m_settingsManager;
    
    // Event Handlers
    void OnSave(wxCommandEvent& event);
    void OnReset(wxCommandEvent& event);
    void OnOpenFolder(wxCommandEvent& event);
    void OnThemeChange(wxCommandEvent& event);
    
    // Helper Methods
    void CreateControls();
    void LayoutControls();
    void ApplyTheme(const wxString& theme);
    
    wxDECLARE_EVENT_TABLE();
};
