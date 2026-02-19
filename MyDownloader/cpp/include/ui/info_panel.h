#pragma once

#include <wx/wx.h>
#include <wx/hyperlink.h>

/**
 * Info Panel - Application information and help
 */
class InfoPanel : public wxPanel
{
public:
    InfoPanel(wxWindow* parent);
    virtual ~InfoPanel();

private:
    // UI Components
    wxStaticText* m_versionLabel;
    wxStaticText* m_descriptionLabel;
    wxHyperlinkCtrl* m_githubLink;
    wxHyperlinkCtrl* m_licenseLink;
    
    wxTextCtrl* m_featuresText;
    wxTextCtrl* m_creditsText;
    
    wxButton* m_checkUpdatesButton;
    wxButton* m_openDocsButton;
    
    // Event Handlers
    void OnCheckUpdates(wxCommandEvent& event);
    void OnOpenDocs(wxCommandEvent& event);
    
    // Helper Methods
    void CreateControls();
    void LayoutControls();
    void LoadApplicationInfo();
    
    wxDECLARE_EVENT_TABLE();
};
