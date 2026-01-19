import { useEffect, useState } from 'react';
import './App.css';

interface PanelProps {
  title: string;
  loading?: boolean;
  isEmpty?: boolean;
  emptyMessage?: string;
  children: React.ReactNode;
}

interface SmartMoneyItem {
  user_id: string;
  roi: number;
  win_rate: number;
  profit: number;
  trade_count: number;
}

interface WhaleItem {
  user_id: string;
  net_invested: number;
}

interface ProfitItem {
  user_id: string;
  profit: number;
}

interface HotMarketItem {
  market_id: string;
  question: string;
  volume: number;
}

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000';

const DashboardPanel = ({ title, loading, isEmpty, emptyMessage, children }: PanelProps) => {
  return (
    <div className="panel">
      <div className="panel-header">
        <span className="panel-title">{title}</span>
        {loading && <div className="status-dot" style={{ animation: 'pulse 1s infinite' }} />}
      </div>
      <div className="panel-content">
        {loading ? (
          <div className="loading-state">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="shimmer" style={{ width: `${Math.random() * 40 + 60}%` }} />
            ))}
          </div>
        ) : isEmpty ? (
          <div className="empty-state">
            <div className="empty-icon">∅</div>
            <div>{emptyMessage || 'No data available'}</div>
          </div>
        ) : (
          children
        )}
      </div>
    </div>
  );
};

const formatPercent = (value: number) => `${(value * 100).toFixed(2)}%`;
const formatUsd = (value: number) => `$${value.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;

const SmartMoneySection = ({ items }: { items: SmartMoneyItem[] }) => (
  <table className="data-table">
    <thead>
      <tr>
        <th>Wallet</th>
        <th>ROI</th>
        <th>Win Rate</th>
        <th>Profit</th>
        <th>Trades</th>
      </tr>
    </thead>
    <tbody>
      {items.map((item) => (
        <tr key={item.user_id}>
          <td style={{ fontFamily: 'var(--font-mono)' }}>{item.user_id}</td>
          <td>{formatPercent(item.roi)}</td>
          <td>{formatPercent(item.win_rate)}</td>
          <td className={item.profit >= 0 ? 'profit-positive' : 'profit-negative'}>
            {formatUsd(item.profit)}
          </td>
          <td>{item.trade_count}</td>
        </tr>
      ))}
    </tbody>
  </table>
);

const WhalesSection = ({ items }: { items: WhaleItem[] }) => (
  <table className="data-table">
    <thead>
      <tr>
        <th>Wallet</th>
        <th>Net Invested (24h)</th>
      </tr>
    </thead>
    <tbody>
      {items.map((item) => (
        <tr key={item.user_id}>
          <td style={{ fontFamily: 'var(--font-mono)' }}>{item.user_id}</td>
          <td className="profit-positive">{formatUsd(item.net_invested)}</td>
        </tr>
      ))}
    </tbody>
  </table>
);

const TopProfitSection = ({ items }: { items: ProfitItem[] }) => (
  <table className="data-table">
    <thead>
      <tr>
        <th>Rank</th>
        <th>User</th>
        <th>Total Profit</th>
      </tr>
    </thead>
    <tbody>
      {items.map((item, index) => (
        <tr key={item.user_id}>
          <td style={{ color: index === 0 ? 'gold' : index === 1 ? 'silver' : index === 2 ? '#cd7f32' : 'inherit' }}>
            #{index + 1}
          </td>
          <td>{item.user_id}</td>
          <td className={item.profit >= 0 ? 'profit-positive' : 'profit-negative'}>
            {formatUsd(item.profit)}
          </td>
        </tr>
      ))}
    </tbody>
  </table>
);

const HotMarketsSection = ({ items }: { items: HotMarketItem[] }) => (
  <div style={{ display: 'grid', gap: '8px' }}>
    {items.map((item) => (
      <div
        key={item.market_id}
        style={{
          padding: '12px',
          border: '1px solid var(--border-color)',
          borderRadius: '4px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <div>
          <div style={{ fontSize: '0.9rem', marginBottom: '4px' }}>{item.question || item.market_id}</div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>Vol: {formatUsd(item.volume)}</div>
        </div>
        <div style={{ color: 'var(--accent-hot)', fontWeight: 'bold' }}>Hot</div>
      </div>
    ))}
  </div>
);

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

function App() {
  const [smartMoney, setSmartMoney] = useState<SmartMoneyItem[]>([]);
  const [whales, setWhales] = useState<WhaleItem[]>([]);
  const [topProfit, setTopProfit] = useState<ProfitItem[]>([]);
  const [hotMarkets, setHotMarkets] = useState<HotMarketItem[]>([]);

  const [loadingSmartMoney, setLoadingSmartMoney] = useState(true);
  const [loadingWhales, setLoadingWhales] = useState(true);
  const [loadingTopProfit, setLoadingTopProfit] = useState(true);
  const [loadingHotMarkets, setLoadingHotMarkets] = useState(true);

  const [smartMoneyError, setSmartMoneyError] = useState<string | null>(null);
  const [whalesError, setWhalesError] = useState<string | null>(null);
  const [topProfitError, setTopProfitError] = useState<string | null>(null);
  const [hotMarketsError, setHotMarketsError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const loadAll = async () => {
      setLoadingSmartMoney(true);
      setLoadingWhales(true);
      setLoadingTopProfit(true);
      setLoadingHotMarkets(true);
      setSmartMoneyError(null);
      setWhalesError(null);
      setTopProfitError(null);
      setHotMarketsError(null);

      try {
        const [smart, whale, profit, hot] = await Promise.all([
          fetchJson<{ data: SmartMoneyItem[] }>('/monitor/smart-money'),
          fetchJson<{ data: WhaleItem[] }>('/monitor/whales'),
          fetchJson<{ data: ProfitItem[] }>('/rankings/top-profit'),
          fetchJson<{ data: HotMarketItem[] }>('/markets/hot'),
        ]);
        if (!isMounted) {
          return;
        }
        setSmartMoney(smart.data || []);
        setWhales(whale.data || []);
        setTopProfit(profit.data || []);
        setHotMarkets(hot.data || []);
      } catch (error) {
        if (!isMounted) {
          return;
        }
        const message = error instanceof Error ? error.message : 'Failed to load data';
        setSmartMoneyError(message);
        setWhalesError(message);
        setTopProfitError(message);
        setHotMarketsError(message);
      } finally {
        if (isMounted) {
          setLoadingSmartMoney(false);
          setLoadingWhales(false);
          setLoadingTopProfit(false);
          setLoadingHotMarkets(false);
        }
      }
    };

    loadAll();
    const interval = setInterval(loadAll, 30000);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <>
      <header>
        <div className="brand">
          POLYMARKET<span>KIT</span>
        </div>
        <div className="status-indicator">
          <div className="status-dot"></div>
          LIVE
        </div>
      </header>

      <main className="dashboard-grid">
        <DashboardPanel
          title="Smart Money Flow"
          loading={loadingSmartMoney}
          isEmpty={!loadingSmartMoney && smartMoney.length === 0}
          emptyMessage={smartMoneyError || 'No smart money data'}
        >
          <SmartMoneySection items={smartMoney} />
        </DashboardPanel>

        <DashboardPanel
          title="Whale Watch"
          loading={loadingWhales}
          isEmpty={!loadingWhales && whales.length === 0}
          emptyMessage={whalesError || 'No whale data'}
        >
          <WhalesSection items={whales} />
        </DashboardPanel>

        <DashboardPanel
          title="Top Profit (30d)"
          loading={loadingTopProfit}
          isEmpty={!loadingTopProfit && topProfit.length === 0}
          emptyMessage={topProfitError || 'No profit data'}
        >
          <TopProfitSection items={topProfit} />
        </DashboardPanel>

        <DashboardPanel
          title="Hot Markets"
          loading={loadingHotMarkets}
          isEmpty={!loadingHotMarkets && hotMarkets.length === 0}
          emptyMessage={hotMarketsError || 'No hot markets data'}
        >
          <HotMarketsSection items={hotMarkets} />
        </DashboardPanel>
      </main>
    </>
  );
}

export default App;
