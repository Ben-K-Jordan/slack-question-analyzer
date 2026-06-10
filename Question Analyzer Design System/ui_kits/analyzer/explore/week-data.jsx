// Real Week-in-Review data, grouped from the IBM webMethods MFT/IWHI Slack threads.
// Week of Jun 2–8, 2026.
window.WEEK_DATA = {
  weekLabel: 'Jun 2 – 8, 2026',
  totalThisWeek: 22,
  totalLastWeek: 18,
  deltaPct: +18,          // vs last week
  newQuestionTypes: 5,    // groups that didn't appear last week
  groupsThisWeek: 8,
  answered: 3,
  // 6-week volume trend (oldest → newest), newest = this week
  trend: [14, 12, 19, 16, 18, 22],
  trendLabels: ['Apr 28', 'May 5', 'May 12', 'May 19', 'May 26', 'Jun 2'],
  // movement: 'new' | number (rank change vs last week, + = rose)
  groups: [
    {
      rank: 1, count: 4, similarity: '90%', movement: 'new',
      topic: 'Antivirus scanning',
      question: 'How do I configure virus scanning in MFT and handle failures?',
      keywords: ['mft', 'antivirus', 'quarantine', 'notification'],
      questions: [
        { text: 'Copy Task to target failing: "Exception while scanning for virus" — please advise.', date: 'Jun 5' },
        { text: 'When a virus is detected, how can we send an email notification to an admin?', date: 'Jun 5' },
        { text: 'Post-processing virus scanner → move file to quarantine or approved folder + send mail?', date: 'Jun 2' },
        { text: 'Can a post-processing script return a custom error to drive quarantine vs approve?', date: 'Jun 2' },
      ],
    },
    {
      rank: 2, count: 3, similarity: '88%', movement: 'new',
      topic: 'Metering & usage stats',
      question: 'How can customers measure MFT transaction statistics without the metering server?',
      keywords: ['metering', 'transactions', 'usage', 'entitlements'],
      questions: [
        { text: 'How to check own transaction stats (inbound/outbound counts, file sizes) beyond metering reports?', date: 'May 30' },
        { text: 'In the absence of a metering server, how can a customer estimate MFT transactions?', date: 'Jun 2' },
        { text: 'Does the wM Metering Agent come pre-installed with the Capabilities Container images for MFT?', date: 'Jun 9' },
      ],
    },
    {
      rank: 3, count: 2, similarity: '86%', movement: +2,
      topic: 'Scheduled Action APIs',
      question: 'Is there a REST API to trigger or deactivate Scheduled Actions?',
      keywords: ['rest-api', 'scheduled-actions', 'automation'],
      questions: [
        { text: 'Is there a REST API to deactivate a list of Scheduled and Post-Processing Actions?', date: 'Jun 5' },
        { text: 'Can we trigger a file transfer via a REST API call instead of a scheduled action?', date: 'Jun 3' },
      ],
    },
    {
      rank: 4, count: 2, similarity: '84%', movement: 'new',
      topic: 'MFT UI errors after upgrade',
      question: 'Internal error / NullPointerException opening the MFT UI after a 12.x install',
      keywords: ['mft-ui', 'upgrade', 'error', 'nullpointer'],
      questions: [
        { text: 'Just installed v12, cannot open MFT UI — MFTServiceException "internal error".', date: 'Jun 3' },
        { text: 'Debug log: NullPointerException — Datastore.logger is null while fetching UI settings.', date: 'Jun 3' },
      ],
    },
    {
      rank: 5, count: 1, similarity: '—', movement: -1,
      topic: 'Azure Blob auth',
      question: 'Azure Blob Container-level SAS token authorization failure',
      keywords: ['azure', 'sas-token', 'authorization'],
      questions: [
        { text: 'Storage-account token works but Container-level SAS token fails authorization — do we support it?', date: 'Jun 5' },
      ],
    },
    {
      rank: 6, count: 1, similarity: '—', movement: 'new',
      topic: 'Control-file triggers',
      question: 'Use a control (.ctrl) file to trigger transfer once the data file is ready',
      keywords: ['find-task', 'control-file', 'trigger'],
      questions: [
        { text: 'On finding {name}.ctrl, move {name}.dat to the destination — can Find/Move tasks do this?', date: 'Jun 5' },
      ],
    },
    {
      rank: 7, count: 1, similarity: '—', movement: -3,
      topic: 'Monitoring & alerting',
      question: 'IWHI end-to-end monitoring & alerting best practices',
      keywords: ['iwhi', 'monitoring', 'alerting'],
      questions: [
        { text: 'Best way to monitor a single app and alert on the first error — one group per B2B/IS/MFT?', date: 'Jun 9' },
      ],
    },
    {
      rank: 8, count: 1, similarity: '—', movement: +1,
      topic: 'Thread exhaustion',
      question: 'Avoiding thread exhaustion with thousands of scheduled actions',
      keywords: ['threads', 'scheduler', 'scaling'],
      questions: [
        { text: '8,600 scheduled actions on a 2-node cluster — how to avoid running out of threads?', date: 'Jun 5' },
      ],
    },
  ],
};
