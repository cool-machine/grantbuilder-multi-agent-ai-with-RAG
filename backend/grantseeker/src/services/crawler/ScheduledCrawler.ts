import { GrantCrawler, CrawlResult } from './GrantCrawler';

export interface CrawlSchedule {
  id: string;
  name: string;
  cronExpression: string;
  sources: string[];
  isActive: boolean;
  lastRun?: string;
  nextRun?: string;
}

export class ScheduledCrawler {
  private crawler: GrantCrawler;
  private schedules: CrawlSchedule[] = [];
  private intervals: Map<string, NodeJS.Timeout> = new Map();

  constructor(crawler: GrantCrawler) {
    this.crawler = crawler;
    this.initializeDefaultSchedules();
  }

  private initializeDefaultSchedules() {
    this.schedules = [
      {
        id: 'daily-government',
        name: 'Daily Government Sources',
        cronExpression: '0 6 * * *', // 6 AM daily
        sources: ['data-gouv-fr'],
        isActive: true
      },
      {
        id: 'weekly-eu',
        name: 'Weekly EU Sources',
        cronExpression: '0 8 * * 1', // 8 AM every Monday
        sources: ['ec-europa-funding'],
        isActive: true
      },
      {
        id: 'bi-weekly-foundations',
        name: 'Bi-weekly Foundation Sources',
        cronExpression: '0 10 */14 * *', // 10 AM every 14 days
        sources: ['fondation-de-france'],
        isActive: true
      }
    ];
  }

  startScheduler() {
    for (const schedule of this.schedules.filter(s => s.isActive)) {
      this.scheduleJob(schedule);
    }
  }

  stopScheduler() {
    for (const [scheduleId, interval] of this.intervals) {
      clearInterval(interval);
    }
    this.intervals.clear();
  }

  private scheduleJob(schedule: CrawlSchedule) {
    // Simple interval-based scheduling (in production, use node-cron)
    const intervalMs = this.cronToInterval(schedule.cronExpression);
    
    const interval = setInterval(async () => {
      console.log(`Running scheduled crawl: ${schedule.name}`);
      
      try {
        // Update last run time
        schedule.lastRun = new Date().toISOString();
        
        // Run crawl for specified sources
        const results: CrawlResult[] = [];
        const sources = this.crawler.getSources().filter(s => 
          schedule.sources.includes(s.id) && s.isActive
        );
        
        for (const source of sources) {
          const result = await this.crawler.crawlSource(source);
          results.push(result);
        }
        
        console.log(`Scheduled crawl completed: ${schedule.name}`, results);
        
        // Calculate next run time
        schedule.nextRun = new Date(Date.now() + intervalMs).toISOString();
        
      } catch (error) {
        console.error(`Scheduled crawl failed: ${schedule.name}`, error);
      }
    }, intervalMs);
    
    this.intervals.set(schedule.id, interval);
    
    // Set initial next run time
    schedule.nextRun = new Date(Date.now() + intervalMs).toISOString();
  }

  private cronToInterval(cronExpression: string): number {
    // Simplified cron parsing - in production, use a proper cron library
    const parts = cronExpression.split(' ');
    
    // Daily pattern: '0 6 * * *' -> 24 hours
    if (parts[2] === '*' && parts[3] === '*' && parts[4] === '*') {
      return 24 * 60 * 60 * 1000; // 24 hours
    }
    
    // Weekly pattern: '0 8 * * 1' -> 7 days
    if (parts[2] === '*' && parts[3] === '*' && parts[4] !== '*') {
      return 7 * 24 * 60 * 60 * 1000; // 7 days
    }
    
    // Bi-weekly pattern: '0 10 */14 * *' -> 14 days
    if (parts[2].includes('*/14')) {
      return 14 * 24 * 60 * 60 * 1000; // 14 days
    }
    
    // Default to daily
    return 24 * 60 * 60 * 1000;
  }

  addSchedule(schedule: CrawlSchedule): void {
    this.schedules.push(schedule);
    if (schedule.isActive) {
      this.scheduleJob(schedule);
    }
  }

  updateSchedule(id: string, updates: Partial<CrawlSchedule>): void {
    const index = this.schedules.findIndex(s => s.id === id);
    if (index !== -1) {
      // Stop existing schedule
      const existingInterval = this.intervals.get(id);
      if (existingInterval) {
        clearInterval(existingInterval);
        this.intervals.delete(id);
      }
      
      // Update schedule
      this.schedules[index] = { ...this.schedules[index], ...updates };
      
      // Restart if active
      if (this.schedules[index].isActive) {
        this.scheduleJob(this.schedules[index]);
      }
    }
  }

  removeSchedule(id: string): void {
    const existingInterval = this.intervals.get(id);
    if (existingInterval) {
      clearInterval(existingInterval);
      this.intervals.delete(id);
    }
    
    this.schedules = this.schedules.filter(s => s.id !== id);
  }

  getSchedules(): CrawlSchedule[] {
    return [...this.schedules];
  }

  getScheduleStatus(): { 
    totalSchedules: number; 
    activeSchedules: number; 
    nextRun?: string;
    runningJobs: number;
  } {
    const activeSchedules = this.schedules.filter(s => s.isActive);
    const nextRuns = activeSchedules
      .map(s => s.nextRun)
      .filter(Boolean)
      .sort();
    
    return {
      totalSchedules: this.schedules.length,
      activeSchedules: activeSchedules.length,
      nextRun: nextRuns[0],
      runningJobs: this.intervals.size
    };
  }
}