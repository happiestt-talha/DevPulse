interface Submission {
  title: string;
  status: string;
  timestamp: number;
  lang: string;
}

export function RecentSubmissionsTable({ submissions }: { submissions: Submission[] }) {
  return (
    <div className="bg-surface rounded-xl border border-border overflow-hidden">
      <div className="px-4 py-3 border-b border-border">
        <h3 className="text-sm font-medium text-textSecondary">Recent Submissions</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-surfaceElevated">
            <tr>
              <th className="px-4 py-2 text-left">Problem</th>
              <th className="px-4 py-2 text-left">Status</th>
              <th className="px-4 py-2 text-left">Language</th>
              <th className="px-4 py-2 text-left">Date</th>
            </tr>
          </thead>
          <tbody>
            {submissions.map((sub, idx) => (
              <tr key={idx} className="border-t border-border">
                <td className="px-4 py-2">{sub.title}</td>
                <td className="px-4 py-2">
                  <span className={sub.status === 'Accepted' ? 'text-green' : 'text-red'}>
                    {sub.status}
                  </span>
                </td>
                <td className="px-4 py-2">{sub.lang}</td>
                <td className="px-4 py-2">{new Date(sub.timestamp * 1000).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}