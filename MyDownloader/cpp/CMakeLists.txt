cmake_minimum_required(VERSION 3.20)
project(MyDownloader VERSION 3.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# wxWidgets finden
find_package(wxWidgets REQUIRED COMPONENTS core base adv net)
include(${wxWidgets_USE_FILE})

# nlohmann/json für JSON-Parsing
find_package(nlohmann_json 3.11.0 REQUIRED)

# cpr für HTTP-Requests (oder libcurl direkt)
find_package(cpr REQUIRED)

# Source-Dateien
set(SOURCES
    src/main.cpp
    src/app.cpp
    src/ui/main_frame.cpp
    src/ui/download_panel.cpp
    src/ui/queue_panel.cpp
    src/ui/history_panel.cpp
    src/ui/settings_panel.cpp
    src/ui/info_panel.cpp
    src/core/downloader.cpp
    src/core/queue_manager.cpp
    src/core/settings_manager.cpp
    src/core/history_manager.cpp
    src/utils/file_utils.cpp
    src/utils/string_utils.cpp
)

# Header-Dateien
set(HEADERS
    include/app.h
    include/ui/main_frame.h
    include/ui/download_panel.h
    include/ui/queue_panel.h
    include/ui/history_panel.h
    include/ui/settings_panel.h
    include/ui/info_panel.h
    include/core/downloader.h
    include/core/queue_manager.h
    include/core/settings_manager.h
    include/core/history_manager.h
    include/utils/file_utils.h
    include/utils/string_utils.h
)

# Executable erstellen
if(WIN32)
    add_executable(MyDownloader WIN32 ${SOURCES} ${HEADERS})
elseif(APPLE)
    add_executable(MyDownloader MACOSX_BUNDLE ${SOURCES} ${HEADERS})
else()
    add_executable(MyDownloader ${SOURCES} ${HEADERS})
endif()

# Include-Verzeichnisse
target_include_directories(MyDownloader PRIVATE 
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

# Libraries linken
target_link_libraries(MyDownloader 
    ${wxWidgets_LIBRARIES}
    nlohmann_json::nlohmann_json
    cpr::cpr
)

# Platform-spezifische Einstellungen
if(WIN32)
    # Windows-spezifische Flags
    target_compile_definitions(MyDownloader PRIVATE 
        _CRT_SECURE_NO_WARNINGS
        UNICODE
        _UNICODE
    )
    # Windows Manifest und Icon
    target_sources(MyDownloader PRIVATE resources/windows/app.rc)
elseif(APPLE)
    # macOS-spezifische Einstellungen
    set_target_properties(MyDownloader PROPERTIES
        MACOSX_BUNDLE_INFO_PLIST ${CMAKE_CURRENT_SOURCE_DIR}/resources/macos/Info.plist
        MACOSX_BUNDLE_BUNDLE_NAME "MyDownloader"
        MACOSX_BUNDLE_GUI_IDENTIFIER "com.urbantke.mydownloader"
        MACOSX_BUNDLE_BUNDLE_VERSION ${PROJECT_VERSION}
        MACOSX_BUNDLE_SHORT_VERSION_STRING ${PROJECT_VERSION}
        MACOSX_BUNDLE_ICON_FILE "app.icns"
    )
    # Icon in Bundle kopieren
    set(MACOSX_BUNDLE_ICON resources/macos/app.icns)
    set_source_files_properties(${MACOSX_BUNDLE_ICON} PROPERTIES
        MACOSX_PACKAGE_LOCATION "Resources"
    )
    target_sources(MyDownloader PRIVATE ${MACOSX_BUNDLE_ICON})
elseif(UNIX)
    # Linux-spezifische Einstellungen
    install(TARGETS MyDownloader RUNTIME DESTINATION bin)
    install(FILES resources/linux/mydownloader.desktop 
            DESTINATION share/applications)
    install(FILES resources/linux/icon.png 
            DESTINATION share/icons/hicolor/256x256/apps 
            RENAME mydownloader.png)
endif()

# Installation
install(TARGETS MyDownloader
    BUNDLE DESTINATION .
    RUNTIME DESTINATION bin
)
