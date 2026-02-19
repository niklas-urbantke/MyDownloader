#include "core/queue_manager.h"

QueueManager::QueueManager()
    : m_isRunning(false),
      m_shouldStop(false),
      m_nextId(1),
      m_completedCount(0),
      m_failedCount(0)
{
    m_downloader = std::make_unique<Downloader>();
}

QueueManager::~QueueManager()
{
    StopQueue();
    if (m_queueThread && m_queueThread->joinable())
    {
        m_queueThread->join();
    }
}

int QueueManager::AddToQueue(const DownloadConfig& config, const std::string& title)
{
    std::lock_guard<std::mutex> lock(m_queueMutex);
    
    QueueItem item;
    item.id = m_nextId++;
    item.config = config;
    item.title = title;
    item.status = "waiting";
    item.progress = 0;
    
    m_queue.push(item);
    m_allItems.push_back(item);
    
    return item.id;
}

void QueueManager::RemoveFromQueue(int id)
{
    // TODO: Implement
}

void QueueManager::ClearQueue()
{
    std::lock_guard<std::mutex> lock(m_queueMutex);
    while (!m_queue.empty())
    {
        m_queue.pop();
    }
    m_allItems.clear();
}

void QueueManager::MoveUp(int id)
{
    // TODO: Implement
}

void QueueManager::MoveDown(int id)
{
    // TODO: Implement
}

void QueueManager::StartQueue()
{
    if (m_isRunning) return;
    
    m_shouldStop = false;
    m_queueThread = std::make_unique<std::thread>(&QueueManager::QueueProcessThread, this);
}

void QueueManager::PauseQueue()
{
    m_shouldStop = true;
}

void QueueManager::StopQueue()
{
    m_shouldStop = true;
}

int QueueManager::GetQueueSize() const
{
    std::lock_guard<std::mutex> lock(m_queueMutex);
    return static_cast<int>(m_queue.size());
}

std::vector<QueueItem> QueueManager::GetAllItems() const
{
    std::lock_guard<std::mutex> lock(m_queueMutex);
    return m_allItems;
}

QueueItem QueueManager::GetItem(int id) const
{
    std::lock_guard<std::mutex> lock(m_queueMutex);
    for (const auto& item : m_allItems)
    {
        if (item.id == id)
            return item;
    }
    return QueueItem();
}

void QueueManager::SaveQueue(const std::string& filename)
{
    // TODO: Implement
}

void QueueManager::LoadQueue(const std::string& filename)
{
    // TODO: Implement
}

void QueueManager::QueueProcessThread()
{
    m_isRunning = true;
    
    while (!m_shouldStop)
    {
        if (m_queue.empty())
        {
            break;
        }
        
        ProcessNextItem();
    }
    
    if (m_completeCallback)
    {
        m_completeCallback();
    }
    
    m_isRunning = false;
}

void QueueManager::ProcessNextItem()
{
    QueueItem item;
    
    {
        std::lock_guard<std::mutex> lock(m_queueMutex);
        if (m_queue.empty()) return;
        
        item = m_queue.front();
        m_queue.pop();
    }
    
    UpdateItemStatus(item.id, "downloading", 0);
    
    // TODO: Actually download using m_downloader
    
    UpdateItemStatus(item.id, "completed", 100);
    m_completedCount++;
}

void QueueManager::UpdateItemStatus(int id, const std::string& status, int progress)
{
    std::lock_guard<std::mutex> lock(m_queueMutex);
    
    for (auto& item : m_allItems)
    {
        if (item.id == id)
        {
            item.status = status;
            item.progress = progress;
            
            if (m_statusCallback)
            {
                m_statusCallback(item);
            }
            break;
        }
    }
}
