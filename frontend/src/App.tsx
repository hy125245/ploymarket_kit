import { useEffect, useState } from 'react';
import './App.css';

interface PanelProps {
  title: React.ReactNode;
  loading?: boolean;
  isEmpty?: boolean;
  emptyMessage?: string;
  children: React.ReactNode;
  controls?: React.ReactNode;
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

interface SuspiciousWalletItem {
  user_id: string;
  reason: string;
  market_id: string;
  stake: number;
  first_trade_at?: string;
  profit_hit_at?: string;
}

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000';

const DashboardPanel = ({ title, loading, isEmpty, emptyMessage, children, controls }: PanelProps) => {
  return (
    <div className="panel">
      <div className="panel-header">
        <span className="panel-title">{title}</span>
        {loading && <div className="status-dot" style={{ animation: 'pulse 1s infinite' }} />}
      </div>
      <div className="panel-content">
        {controls && <div style={{ marginBottom: '12px' }}>{controls}</div>}
        {loading ? (
          <div className="loading-state">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="shimmer" style={{ width: `${Math.random() * 40 + 60}%` }} />
            ))}
          </div>
        ) : isEmpty ? (
          <div className="empty-state">
            <div className="empty-icon">∅</div>
            <div>{emptyMessage || '暂无数据'}</div>
          </div>
        ) : (
          children
        )}
      </div>
    </div>
  );
};

const FilterInput = ({ label, value, onChange, min, max }: { label: string; value: number; onChange: (val: number) => void; min?: number; max?: number }) => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', flex: 1, minWidth: '80px' }}>
    <label style={{ fontSize: '0.75rem', color: 'var(--text-dim)', whiteSpace: 'nowrap' }}>{label}</label>
    <input
      type="number"
      value={value}
      onChange={(e) => onChange(Number(e.target.value))}
      min={min}
      max={max}
      style={{
        background: 'rgba(255, 255, 255, 0.05)',
        border: '1px solid var(--border-color)',
        borderRadius: '4px',
        color: 'inherit',
        padding: '4px 8px',
        fontSize: '0.85rem',
        width: '100%',
        boxSizing: 'border-box'
      }}
    />
  </div>
);

const formatPercent = (value: number) => `${(value * 100).toFixed(2)}%`;
const formatUsd = (value: number) => `$${value.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;

const SmartMoneySection = ({ items }: { items: SmartMoneyItem[] }) => (
  <table className="data-table">
    <thead>
      <tr>
        <th>钱包</th>
        <th>投资回报率</th>
        <th>胜率</th>
        <th>收益</th>
        <th>交易次数</th>
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
        <th>钱包</th>
        <th>净投资额（24小时）</th>
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
        <th>排名</th>
        <th>用户</th>
        <th>总收益</th>
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

const SuspiciousWalletsSection = ({ items }: { items: SuspiciousWalletItem[] }) => (
  <table className="data-table">
    <thead>
      <tr>
        <th>钱包</th>
        <th>原因</th>
        <th>金额</th>
        <th>首次交易</th>
        <th>市场ID</th>
      </tr>
    </thead>
    <tbody>
      {items.map((item, i) => (
        <tr key={`${item.user_id}-${i}`}>
          <td style={{ fontFamily: 'var(--font-mono)' }} title={item.user_id}>
            {item.user_id.slice(0, 6)}...{item.user_id.slice(-4)}
          </td>
          <td>
            {item.reason === 'new_account_large_bet' ? '新号大额' : item.reason}
          </td>
          <td>{formatUsd(item.stake)}</td>
          <td style={{ fontSize: '0.9em' }}>
            {item.first_trade_at 
              ? new Date(item.first_trade_at).toLocaleString('zh-CN', {
                  month: 'numeric',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })
              : '-'}
          </td>
          <td style={{ fontFamily: 'var(--font-mono)' }} title={item.market_id}>
            {item.market_id.slice(0, 4)}...
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
          <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>交易量：{formatUsd(item.volume)}</div>
        </div>
        <div style={{ color: 'var(--accent-hot)', fontWeight: 'bold' }}>热门</div>
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
  const [suspiciousWallets, setSuspiciousWallets] = useState<SuspiciousWalletItem[]>([]);

  const getParam = (key: string, def: number) => {
    const val = new URLSearchParams(window.location.search).get(key);
    return val ? (Number(val) || def) : def;
  };

  const [minAgeDays, setMinAgeDays] = useState(() => getParam('account_age_days', 30));
  const [minStake, setMinStake] = useState(() => getParam('large_stake', 10000));
  const [minProfit, setMinProfit] = useState(() => getParam('profit_threshold', 10000));
  const [reinvestMin, setReinvestMin] = useState(() => getParam('reinvest_min_days', 1));
  const [reinvestMax, setReinvestMax] = useState(() => getParam('reinvest_max_days', 30));

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    params.set('account_age_days', minAgeDays.toString());
    params.set('large_stake', minStake.toString());
    params.set('profit_threshold', minProfit.toString());
    params.set('reinvest_min_days', reinvestMin.toString());
    params.set('reinvest_max_days', reinvestMax.toString());
    const newUrl = `${window.location.pathname}?${params.toString()}`;
    window.history.replaceState(null, '', newUrl);
  }, [minAgeDays, minStake, minProfit, reinvestMin, reinvestMax]);

  const [loadingSmartMoney, setLoadingSmartMoney] = useState(true);
  const [loadingWhales, setLoadingWhales] = useState(true);
  const [loadingTopProfit, setLoadingTopProfit] = useState(true);
  const [loadingHotMarkets, setLoadingHotMarkets] = useState(true);
  const [loadingSuspiciousWallets, setLoadingSuspiciousWallets] = useState(true);

  const [smartMoneyError, setSmartMoneyError] = useState<string | null>(null);
  const [whalesError, setWhalesError] = useState<string | null>(null);
  const [topProfitError, setTopProfitError] = useState<string | null>(null);
  const [hotMarketsError, setHotMarketsError] = useState<string | null>(null);
  const [suspiciousWalletsError, setSuspiciousWalletsError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const loadAll = async () => {
      setLoadingSmartMoney(true);
      setLoadingWhales(true);
      setLoadingTopProfit(true);
      setLoadingHotMarkets(true);
      setLoadingSuspiciousWallets(true);
      setSmartMoneyError(null);
      setWhalesError(null);
      setTopProfitError(null);
      setHotMarketsError(null);
      setSuspiciousWalletsError(null);

      try {
        const suspiciousParams = new URLSearchParams({
          account_age_days: minAgeDays.toString(),
          large_stake: minStake.toString(),
          profit_threshold: minProfit.toString(),
          reinvest_min_days: reinvestMin.toString(),
          reinvest_max_days: reinvestMax.toString(),
        });

        const [smart, whale, profit, hot, suspicious] = await Promise.all([
          fetchJson<{ data: SmartMoneyItem[] }>('/monitor/smart-money'),
          fetchJson<{ data: WhaleItem[] }>('/monitor/whales'),
          fetchJson<{ data: ProfitItem[] }>('/rankings/top-profit'),
          fetchJson<{ data: HotMarketItem[] }>('/markets/hot'),
          fetchJson<{ data: SuspiciousWalletItem[] }>(`/monitor/suspicious-wallets?${suspiciousParams}`),
        ]);
        if (!isMounted) {
          return;
        }
        setSmartMoney(smart.data || []);
        setWhales(whale.data || []);
        setTopProfit(profit.data || []);
        setHotMarkets(hot.data || []);
        setSuspiciousWallets(suspicious.data || []);
      } catch (error) {
        if (!isMounted) {
          return;
        }
        const message = error instanceof Error ? error.message : '加载数据失败';
        setSmartMoneyError(message);
        setWhalesError(message);
        setTopProfitError(message);
        setHotMarketsError(message);
        setSuspiciousWalletsError(message);
      } finally {
        if (isMounted) {
          setLoadingSmartMoney(false);
          setLoadingWhales(false);
          setLoadingTopProfit(false);
          setLoadingHotMarkets(false);
          setLoadingSuspiciousWallets(false);
        }
      }
    };

    loadAll();
    const interval = setInterval(loadAll, 30000);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [minAgeDays, minStake, minProfit, reinvestMin, reinvestMax]);

  return (
    <>
      <header>
        <div className="brand">
          POLYMARKET<span>KIT</span>
        </div>
        <div className="status-indicator">
          <div className="status-dot"></div>
          实时
        </div>
      </header>

      <main className="dashboard-grid">
        <DashboardPanel
          title="聪明资金流向"
          loading={loadingSmartMoney}
          isEmpty={!loadingSmartMoney && smartMoney.length === 0}
          emptyMessage={smartMoneyError || '暂无聪明资金数据'}
        >
          <SmartMoneySection items={smartMoney} />
        </DashboardPanel>

        <DashboardPanel
          title="巨鲸监控"
          loading={loadingWhales}
          isEmpty={!loadingWhales && whales.length === 0}
          emptyMessage={whalesError || '暂无巨鲸数据'}
        >
          <WhalesSection items={whales} />
        </DashboardPanel>

        <DashboardPanel
          title="收益榜（30天）"
          loading={loadingTopProfit}
          isEmpty={!loadingTopProfit && topProfit.length === 0}
          emptyMessage={topProfitError || '暂无收益数据'}
        >
          <TopProfitSection items={topProfit} />
        </DashboardPanel>

        <DashboardPanel
          title={
            <span style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
              可疑钱包监控
              <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontWeight: 'normal', fontFamily: 'var(--font-mono)' }}>
                (Age&gt;{minAgeDays}d Stake&gt;{formatUsd(minStake)} Profit&gt;{formatUsd(minProfit)} Reinv:{reinvestMin}-{reinvestMax}d)
              </span>
            </span>
          }
          loading={loadingSuspiciousWallets}
          isEmpty={!loadingSuspiciousWallets && suspiciousWallets.length === 0}
          emptyMessage={suspiciousWalletsError || '暂无可疑钱包数据'}
          controls={
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              <FilterInput label="账号天数" value={minAgeDays} onChange={setMinAgeDays} min={1} />
              <FilterInput label="大额阈值($)" value={minStake} onChange={setMinStake} min={0} />
              <FilterInput label="利润阈值($)" value={minProfit} onChange={setMinProfit} min={0} />
              <FilterInput 
                label="复投Min(天)" 
                value={reinvestMin} 
                onChange={(v) => {
                  if (v <= reinvestMax) setReinvestMin(v);
                }} 
                min={0} 
                max={reinvestMax}
              />
              <FilterInput 
                label="复投Max(天)" 
                value={reinvestMax} 
                onChange={(v) => {
                  if (v >= reinvestMin) setReinvestMax(v);
                }} 
                min={reinvestMin} 
              />
            </div>
          }
        >
          <SuspiciousWalletsSection items={suspiciousWallets} />
        </DashboardPanel>

        <DashboardPanel
          title="热门市场"
          loading={loadingHotMarkets}
          isEmpty={!loadingHotMarkets && hotMarkets.length === 0}
          emptyMessage={hotMarketsError || '暂无热门市场数据'}
        >
          <HotMarketsSection items={hotMarkets} />
        </DashboardPanel>
      </main>
    </>
  );
}

export default App;
