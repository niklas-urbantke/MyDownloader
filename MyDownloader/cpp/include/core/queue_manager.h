#pragma once

#include "downloader.h"
#include <vector>
#include <queue>
#include <memory>
#include <mutex>

/**
 * Queue item
 */
struct QueueItem
{
    int id;
    DownloadConfig config;
    std::string title;
    std::string status;         // waiting, downloading, completed, failed
    int progress;
    std::string errorMessage;
};

/**
 * Queue status callback
 */
using QueueStatusCallback = std::function<void(const QueueItem& item)>;
using QueueCompleteCallback = std::function<void()>;

/**
 * Queue Manager - Manages download queue
 */
class QueueManager
{
public:
    QueueManager();
    ~QueueManager();

    // Queue management
    int AddToQueue(const DownloadConfig& config, const std::string& title);
    void RemoveFromQueue(int id);
    void ClearQueue();
    void MoveUp(int id);
    void MoveDown(int id);
    
    // Queue control
    void StartQueue();
    void PauseQueue();
    void StopQueue();
    
    // Status
    bool IsRunning() const { return m_isRunning; }
    int GetQueueSize() const;
    int GetCompletedCount() const { return m_completedCount; }
    int GetFailedCount() const { return m_failedCount; }
    
    // Get items
    std::vector<QueueItem> GetAllItems() const;
    QueueItem GetItem(int id) const;
    
    // Callbacks
    void SetStatusCallback(QueueStatusCallback callback) { m_statusCallback = callback; }
    void SetCompleteCallback(QueueCompleteCallback callback) { m_completeCallback = callback; }
    
    // Save/Load
    void SaveQueue(const std::string& filename);
    void LoadQueue(const std::string& filename);

private:
    std::queue<QueueItem> m_queue;
    std::vector<QueueItem> m_allItems;  // For display
    
    std::atomic<bool> m_isRunning;
    std::atomic<bool> m_shouldStop;
    
    int m_nextId;
    int m_completedCount;
    int m_failedCount;
    
    std::unique_ptr<Downloader> m_downloader;
    std::unique_ptr<std::thread> m_queueThread;
    
    mutable std::mutex m_queueMutex;
    
    QueueStatusCallback m_statusCallback;
    QueueCompleteCallback m_completeCallback;
    
    // Helper methods
    void QueueProcessThread();
    void ProcessNextItem();
    void UpdateItemStatus(int id, const std::string& status, int progress = 0);
};
