import { useState, useRef, useEffect } from "react";
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, CartesianGrid, Legend } from "recharts";

const CATEGORY_RULES = {
  "Food & Dining": ["swiggy", "zomato", "restaurant", "cafe", "pizza", "burger", "food", "dining", "eat", "kitchen", "bakery", "starbucks", "mcdonald", "kfc", "domino", "subway", "biryani", "chai", "coffee", "grocery", "supermarket", "bigbasket", "blinkit", "zepto", "dmart"],
  "Shopping": ["amazon", "flipkart", "myntra", "ajio", "mall", "shop", "store", "retail", "clothing", "fashion", "electronics", "meesho", "nykaa", "tatacliq"],
  "Transport": ["uber", "ola", "rapido", "metro", "petrol", "fuel", "diesel", "parking", "toll", "cab", "auto", "rickshaw", "bus", "train", "irctc", "redbus"],
  "Bills & Utilities": ["electricity", "water", "gas", "broadband", "wifi", "internet", "jio", "airtel", "vi ", "bsnl", "postpaid", "prepaid", "recharge", "dth", "tata play"],
  "Rent & Housing": ["rent", "housing", "maintenance", "society", "flat", "apartment", "lease", "landlord", "pg "],
  "Health": ["hospital", "pharmacy", "medical", "doctor", "clinic", "health", "medicine", "apollo", "practo", "1mg", "pharmeasy", "netmeds", "gym", "fitness"],
  "Entertainment": ["netflix", "hotstar", "prime video", "spotify", "youtube", "movie", "cinema", "pvr", "inox", "gaming", "game", "subscription", "disney"],
  "Education": ["udemy", "coursera", "book", "course", "school", "college", "tuition", "coaching", "unacademy", "byju"],
  "Investment": ["mutual fund", "sip", "stock", "share", "zerodha", "groww", "upstox", "investment", "fd ", "fixed deposit", "ppf", "nps", "gold"],
  "Transfer": ["transfer", "neft", "imps", "upi", "sent to", "paid to", "gpay", "phonepe", "paytm"],
  "Income": ["salary", "credit", "received", "cashback", "refund", "interest earned", "dividend", "bonus"],
  "Other": []
};

const CATEGORY_COLORS = {
  "Food & Dining": "#F97316",
  "Shopping": "#8B5CF6",
  "Transport": "#3B82F6",
  "Bills & Utilities": "#EAB308",
  "Rent & Housing": "#EF4444",
  "Health": "#10B981",
  "Entertainment": "#EC4899",
  "Education": "#06B6D4",
  "Investment": "#6366F1",
  "Transfer": "#78716C",
  "Income": "#22C55E",
  "Other": "#94A3B8"
};

function categorize(description) {
  const lower = (description || "").toLowerCase();
  for (const [category, keywords] of Object.entries(CATEGORY_RULES)) {
    if (category === "Other") continue;
    if (keywords.some(kw => lower.includes(kw))) return category;
  }
  return "Other";
}

function parseCSV(text) {
  const lines = text.trim().split("\n");
  if (lines.length < 2) return [];
  
  const headers = lines[0].split(",").map(h => h.trim().toLowerCase().replace(/['"]/g, ""));
  
  const dateIdx = headers.findIndex(h => /date/.test(h));
  const descIdx = headers.findIndex(h => /desc|narr|particular|remark|detail|memo/.test(h));
  const amountIdx = headers.findIndex(h => /amount|sum|value/.test(h));
  const debitIdx = headers.findIndex(h => /debit|withdrawal|dr/.test(h));
  const creditIdx = headers.findIndex(h => /credit|deposit|cr/.test(h));
  
  if (dateIdx === -1) return [];
  
  const transactions = [];
  
  for (let i = 1; i < lines.length; i++) {
    const vals = lines[i].match(/(".*?"|[^,]+)/g);
    if (!vals) continue;
    const clean = vals.map(v => v.trim().replace(/^"|"$/g, ""));
    
    const dateStr = clean[dateIdx] || "";
    const desc = clean[descIdx] || clean[dateIdx + 1] || "";
    
    let amount = 0;
    let type = "expense";
    
    if (amountIdx !== -1) {
      amount = parseFloat((clean[amountIdx] || "0").replace(/[^0-9.\-]/g, "")) || 0;
      type = amount >= 0 ? "expense" : "income";
      amount = Math.abs(amount);
    } else {
      const debit = parseFloat((clean[debitIdx] || "0").replace(/[^0-9.\-]/g, "")) || 0;
      const credit = parseFloat((clean[creditIdx] || "0").replace(/[^0-9.\-]/g, "")) || 0;
      if (debit > 0) { amount = debit; type = "expense"; }
      else if (credit > 0) { amount = credit; type = "income"; }
    }
    
    const category = categorize(desc);
    if (category === "Income") type = "income";
    
    let parsedDate = new Date(dateStr);
    if (isNaN(parsedDate.getTime())) {
      const parts = dateStr.split(/[\/\-\.]/);
      if (parts.length === 3) {
        parsedDate = new Date(`${parts[2]}-${parts[1]}-${parts[0]}`);
        if (isNaN(parsedDate.getTime())) parsedDate = new Date(`${parts[2]}-${parts[0]}-${parts[1]}`);
      }
    }
    
    if (!isNaN(parsedDate.getTime()) && amount > 0) {
      transactions.push({
        date: parsedDate,
        dateStr: parsedDate.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" }),
        month: parsedDate.toLocaleDateString("en-IN", { month: "short", year: "numeric" }),
        description: desc,
        amount,
        type,
        category
      });
    }
  }
  
  return transactions.sort((a, b) => a.date - b.date);
}

const SAMPLE_CSV = `Date,Description,Debit,Credit
01/01/2026,Salary Credit,,85000
03/01/2026,Rent Payment,22000,
04/01/2026,Swiggy Order,450,
05/01/2026,Amazon Shopping,3200,
06/01/2026,Uber Ride,280,
07/01/2026,Netflix Subscription,649,
08/01/2026,Electricity Bill,1800,
09/01/2026,Zerodha SIP,5000,
10/01/2026,Apollo Pharmacy,560,
12/01/2026,Zomato Order,380,
14/01/2026,Flipkart Purchase,4500,
15/01/2026,Jio Recharge,599,
16/01/2026,Petrol,2000,
18/01/2026,Starbucks Coffee,520,
20/01/2026,Udemy Course,499,
22/01/2026,DMart Grocery,3400,
25/01/2026,PVR Movie Tickets,900,
27/01/2026,Ola Cab,350,
28/01/2026,GPay Transfer,2000,
30/01/2026,Gym Membership,1500,
01/02/2026,Salary Credit,,87000
03/02/2026,Rent Payment,22000,
05/02/2026,Swiggy Order,520,
06/02/2026,BigBasket Grocery,2800,
08/02/2026,Airtel Broadband,999,
10/02/2026,Amazon Electronics,8500,
12/02/2026,Uber Ride,310,
14/02/2026,Restaurant Dinner,2200,
15/02/2026,Groww Mutual Fund,10000,
17/02/2026,Myntra Fashion,3600,
19/02/2026,Medicine Pharmeasy,890,
20/02/2026,Spotify Premium,119,
22/02/2026,Petrol,2200,
24/02/2026,Blinkit Grocery,1600,
26/02/2026,Metro Card Recharge,500,
28/02/2026,Cashback Received,,200
01/03/2026,Salary Credit,,87000
03/03/2026,Rent Payment,22000,
05/03/2026,Zomato Order,680,
07/03/2026,Flipkart Shopping,5200,
09/03/2026,Ola Ride,420,
10/03/2026,Electricity Bill,2100,
12/03/2026,Zerodha SIP,5000,
14/03/2026,Practo Doctor Visit,800,
16/03/2026,Swiggy Order,390,
18/03/2026,Disney+ Hotstar,299,
20/03/2026,Coursera Course,3200,
22/03/2026,DMart Grocery,4100,
24/03/2026,Parking Charges,200,
26/03/2026,Cafe Coffee Day,340,
28/03/2026,GPay Transfer,5000,
30/03/2026,Interest Earned,,450`;

function StatCard({ label, value, sub, color, icon }) {
  return (
    <div style={{
      background: "rgba(255,255,255,0.03)",
      border: "1px solid rgba(255,255,255,0.06)",
      borderRadius: 16,
      padding: "20px 24px",
      flex: 1,
      minWidth: 200,
    }}>
      <div style={{ fontSize: 13, color: "#8B8FA3", letterSpacing: "0.04em", marginBottom: 8, fontFamily: "'DM Sans', sans-serif" }}>{icon} {label}</div>
      <div style={{ fontSize: 28, fontWeight: 700, color, fontFamily: "'Space Mono', monospace", letterSpacing: "-0.02em" }}>
        ₹{typeof value === "number" ? value.toLocaleString("en-IN") : value}
      </div>
      {sub && <div style={{ fontSize: 12, color: "#6B7094", marginTop: 4, fontFamily: "'DM Sans', sans-serif" }}>{sub}</div>}
    </div>
  );
}

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: "#1A1B2E",
      border: "1px solid rgba(255,255,255,0.1)",
      borderRadius: 10,
      padding: "10px 14px",
      fontSize: 13,
      color: "#E2E4F0",
      fontFamily: "'DM Sans', sans-serif",
      boxShadow: "0 8px 32px rgba(0,0,0,0.4)"
    }}>
      <div style={{ fontWeight: 600 }}>{payload[0].name || payload[0].payload?.name || payload[0].payload?.month}</div>
      <div style={{ color: "#F97316", marginTop: 4 }}>₹{payload[0].value?.toLocaleString("en-IN")}</div>
    </div>
  );
}

export default function FinanceDashboard() {
  const [transactions, setTransactions] = useState([]);
  const [view, setView] = useState("overview");
  const [loaded, setLoaded] = useState(false);
  const fileRef = useRef();

  const handleFile = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      const parsed = parseCSV(ev.target.result);
      setTransactions(parsed);
      setLoaded(true);
    };
    reader.readAsText(file);
  };

  const loadSample = () => {
    setTransactions(parseCSV(SAMPLE_CSV));
    setLoaded(true);
  };

  const expenses = transactions.filter(t => t.type === "expense");
  const incomes = transactions.filter(t => t.type === "income");
  const totalExpense = expenses.reduce((s, t) => s + t.amount, 0);
  const totalIncome = incomes.reduce((s, t) => s + t.amount, 0);
  const savings = totalIncome - totalExpense;
  const savingsRate = totalIncome > 0 ? ((savings / totalIncome) * 100).toFixed(1) : 0;

  const byCategory = {};
  expenses.forEach(t => {
    byCategory[t.category] = (byCategory[t.category] || 0) + t.amount;
  });
  const pieData = Object.entries(byCategory)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);

  const byMonth = {};
  transactions.forEach(t => {
    if (!byMonth[t.month]) byMonth[t.month] = { month: t.month, expense: 0, income: 0 };
    if (t.type === "expense") byMonth[t.month].expense += t.amount;
    else byMonth[t.month].income += t.amount;
  });
  const monthlyData = Object.values(byMonth);

  const dailySpend = {};
  expenses.forEach(t => {
    const key = t.date.toISOString().split("T")[0];
    dailySpend[key] = (dailySpend[key] || 0) + t.amount;
  });
  const dailyData = Object.entries(dailySpend).map(([date, amount]) => ({
    date: new Date(date).toLocaleDateString("en-IN", { day: "2-digit", month: "short" }),
    amount
  }));

  const topExpenses = [...expenses].sort((a, b) => b.amount - a.amount).slice(0, 10);
  const avgDaily = expenses.length > 0 ? Math.round(totalExpense / (new Set(expenses.map(t => t.date.toISOString().split("T")[0])).size)) : 0;

  const fontLink = "https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap";

  if (!loaded) {
    return (
      <div style={{
        minHeight: "100vh",
        background: "linear-gradient(145deg, #0D0E1A 0%, #151729 50%, #0D0E1A 100%)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: "'DM Sans', sans-serif",
        padding: 20
      }}>
        <link href={fontLink} rel="stylesheet" />
        <div style={{ textAlign: "center", maxWidth: 520 }}>
          <div style={{ fontSize: 48, marginBottom: 8 }}>💰</div>
          <h1 style={{
            fontSize: 32,
            fontWeight: 700,
            color: "#E2E4F0",
            margin: "0 0 8px",
            fontFamily: "'Space Mono', monospace",
            letterSpacing: "-0.03em"
          }}>
            Finance Pipeline
          </h1>
          <p style={{ color: "#6B7094", fontSize: 15, margin: "0 0 40px", lineHeight: 1.6 }}>
            Upload your bank CSV export and instantly see where your money goes — beautifully visualized.
          </p>

          <div style={{
            background: "rgba(255,255,255,0.03)",
            border: "2px dashed rgba(255,255,255,0.1)",
            borderRadius: 20,
            padding: "48px 32px",
            cursor: "pointer",
            transition: "all 0.3s",
            marginBottom: 16
          }}
            onClick={() => fileRef.current?.click()}
            onMouseEnter={e => { e.currentTarget.style.borderColor = "rgba(249,115,22,0.4)"; e.currentTarget.style.background = "rgba(249,115,22,0.03)"; }}
            onMouseLeave={e => { e.currentTarget.style.borderColor = "rgba(255,255,255,0.1)"; e.currentTarget.style.background = "rgba(255,255,255,0.03)"; }}
          >
            <div style={{ fontSize: 36, marginBottom: 12 }}>📂</div>
            <div style={{ color: "#E2E4F0", fontSize: 16, fontWeight: 600, marginBottom: 6 }}>Drop your bank CSV here</div>
            <div style={{ color: "#6B7094", fontSize: 13 }}>Supports most Indian bank formats (HDFC, SBI, ICICI, Axis, etc.)</div>
            <input ref={fileRef} type="file" accept=".csv,.txt" onChange={handleFile} style={{ display: "none" }} />
          </div>

          <div style={{ color: "#4B5072", fontSize: 13, marginBottom: 20 }}>— or —</div>
          <button onClick={loadSample} style={{
            background: "linear-gradient(135deg, #F97316, #EA580C)",
            color: "#fff",
            border: "none",
            padding: "14px 36px",
            borderRadius: 12,
            fontSize: 15,
            fontWeight: 600,
            cursor: "pointer",
            fontFamily: "'DM Sans', sans-serif",
            transition: "transform 0.2s, box-shadow 0.2s",
            boxShadow: "0 4px 20px rgba(249,115,22,0.3)"
          }}
            onMouseEnter={e => { e.currentTarget.style.transform = "translateY(-2px)"; e.currentTarget.style.boxShadow = "0 8px 30px rgba(249,115,22,0.4)"; }}
            onMouseLeave={e => { e.currentTarget.style.transform = "translateY(0)"; e.currentTarget.style.boxShadow = "0 4px 20px rgba(249,115,22,0.3)"; }}
          >
            ✨ Try with Sample Data
          </button>
          <div style={{ color: "#4B5072", fontSize: 12, marginTop: 16 }}>Your data stays in your browser. Nothing is uploaded anywhere.</div>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: "100vh",
      background: "linear-gradient(145deg, #0D0E1A 0%, #151729 50%, #0D0E1A 100%)",
      fontFamily: "'DM Sans', sans-serif",
      color: "#E2E4F0",
      padding: "24px 20px"
    }}>
      <link href={fontLink} rel="stylesheet" />

      {/* Header */}
      <div style={{ maxWidth: 1100, margin: "0 auto 28px", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 700, margin: 0, fontFamily: "'Space Mono', monospace", letterSpacing: "-0.03em" }}>
            💰 Finance Pipeline
          </h1>
          <p style={{ color: "#6B7094", fontSize: 13, margin: "4px 0 0" }}>{transactions.length} transactions analyzed</p>
        </div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {["overview", "categories", "trends", "transactions"].map(v => (
            <button key={v} onClick={() => setView(v)} style={{
              background: view === v ? "rgba(249,115,22,0.15)" : "rgba(255,255,255,0.03)",
              color: view === v ? "#F97316" : "#8B8FA3",
              border: view === v ? "1px solid rgba(249,115,22,0.3)" : "1px solid rgba(255,255,255,0.06)",
              padding: "8px 18px",
              borderRadius: 10,
              fontSize: 13,
              fontWeight: 600,
              cursor: "pointer",
              fontFamily: "'DM Sans', sans-serif",
              transition: "all 0.2s",
              textTransform: "capitalize"
            }}>{v}</button>
          ))}
          <button onClick={() => { setLoaded(false); setTransactions([]); }} style={{
            background: "rgba(239,68,68,0.1)",
            color: "#EF4444",
            border: "1px solid rgba(239,68,68,0.2)",
            padding: "8px 18px",
            borderRadius: 10,
            fontSize: 13,
            cursor: "pointer",
            fontFamily: "'DM Sans', sans-serif"
          }}>Reset</button>
        </div>
      </div>

      <div style={{ maxWidth: 1100, margin: "0 auto" }}>
        {/* Stat Cards */}
        <div style={{ display: "flex", gap: 16, marginBottom: 28, flexWrap: "wrap" }}>
          <StatCard icon="📥" label="TOTAL INCOME" value={totalIncome} color="#22C55E" />
          <StatCard icon="📤" label="TOTAL SPENT" value={totalExpense} color="#F97316" />
          <StatCard icon="💎" label="SAVINGS" value={savings} sub={`${savingsRate}% savings rate`} color={savings >= 0 ? "#22C55E" : "#EF4444"} />
          <StatCard icon="📊" label="AVG DAILY SPEND" value={avgDaily} color="#3B82F6" />
        </div>

        {/* Overview */}
        {view === "overview" && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
            {/* Pie Chart */}
            <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 16, padding: 24 }}>
              <h3 style={{ fontSize: 15, fontWeight: 600, margin: "0 0 20px", color: "#8B8FA3" }}>Spending by Category</h3>
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie data={pieData} dataKey="value" cx="50%" cy="50%" outerRadius={100} innerRadius={55} paddingAngle={3} strokeWidth={0}>
                    {pieData.map((entry, i) => <Cell key={i} fill={CATEGORY_COLORS[entry.name] || "#94A3B8"} />)}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                </PieChart>
              </ResponsiveContainer>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "6px 16px", marginTop: 12 }}>
                {pieData.map(d => (
                  <div key={d.name} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: "#8B8FA3" }}>
                    <div style={{ width: 8, height: 8, borderRadius: 2, background: CATEGORY_COLORS[d.name] }} />
                    {d.name}
                  </div>
                ))}
              </div>
            </div>

            {/* Monthly Bar Chart */}
            <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 16, padding: 24 }}>
              <h3 style={{ fontSize: 15, fontWeight: 600, margin: "0 0 20px", color: "#8B8FA3" }}>Monthly Income vs Expense</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={monthlyData} barGap={4}>
                  <XAxis dataKey="month" tick={{ fill: "#6B7094", fontSize: 12 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: "#6B7094", fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={v => `₹${(v/1000).toFixed(0)}k`} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="income" fill="#22C55E" radius={[6, 6, 0, 0]} name="Income" />
                  <Bar dataKey="expense" fill="#F97316" radius={[6, 6, 0, 0]} name="Expense" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Daily Spend Line */}
            <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 16, padding: 24, gridColumn: "1 / -1" }}>
              <h3 style={{ fontSize: 15, fontWeight: 600, margin: "0 0 20px", color: "#8B8FA3" }}>Daily Spending Trend</h3>
              <ResponsiveContainer width="100%" height={240}>
                <LineChart data={dailyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                  <XAxis dataKey="date" tick={{ fill: "#6B7094", fontSize: 11 }} axisLine={false} tickLine={false} interval="preserveStartEnd" />
                  <YAxis tick={{ fill: "#6B7094", fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={v => `₹${v.toLocaleString("en-IN")}`} />
                  <Tooltip content={<CustomTooltip />} />
                  <Line type="monotone" dataKey="amount" stroke="#F97316" strokeWidth={2.5} dot={{ fill: "#F97316", r: 3, strokeWidth: 0 }} activeDot={{ r: 6, fill: "#F97316" }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* Categories */}
        {view === "categories" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {pieData.map((cat, i) => {
              const pct = ((cat.value / totalExpense) * 100).toFixed(1);
              const count = expenses.filter(t => t.category === cat.name).length;
              return (
                <div key={cat.name} style={{
                  background: "rgba(255,255,255,0.03)",
                  border: "1px solid rgba(255,255,255,0.06)",
                  borderRadius: 14,
                  padding: "18px 24px",
                  display: "flex",
                  alignItems: "center",
                  gap: 20
                }}>
                  <div style={{ width: 42, height: 42, borderRadius: 12, background: `${CATEGORY_COLORS[cat.name]}20`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14, fontWeight: 700, color: CATEGORY_COLORS[cat.name], fontFamily: "'Space Mono', monospace" }}>
                    #{i + 1}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: 15, marginBottom: 6 }}>{cat.name}</div>
                    <div style={{ background: "rgba(255,255,255,0.05)", borderRadius: 6, height: 8, overflow: "hidden" }}>
                      <div style={{ height: "100%", width: `${pct}%`, background: CATEGORY_COLORS[cat.name], borderRadius: 6, transition: "width 0.6s" }} />
                    </div>
                  </div>
                  <div style={{ textAlign: "right", minWidth: 120 }}>
                    <div style={{ fontFamily: "'Space Mono', monospace", fontWeight: 700, fontSize: 16, color: CATEGORY_COLORS[cat.name] }}>
                      ₹{cat.value.toLocaleString("en-IN")}
                    </div>
                    <div style={{ fontSize: 12, color: "#6B7094" }}>{pct}% · {count} txns</div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Trends */}
        {view === "trends" && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
            <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 16, padding: 24 }}>
              <h3 style={{ fontSize: 15, fontWeight: 600, margin: "0 0 20px", color: "#8B8FA3" }}>Monthly Savings</h3>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={monthlyData.map(m => ({ ...m, savings: m.income - m.expense }))}>
                  <XAxis dataKey="month" tick={{ fill: "#6B7094", fontSize: 12 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: "#6B7094", fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={v => `₹${(v/1000).toFixed(0)}k`} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="savings" radius={[6, 6, 0, 0]} name="Savings">
                    {monthlyData.map((m, i) => <Cell key={i} fill={m.income - m.expense >= 0 ? "#22C55E" : "#EF4444"} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 16, padding: 24 }}>
              <h3 style={{ fontSize: 15, fontWeight: 600, margin: "0 0 20px", color: "#8B8FA3" }}>Top 10 Expenses</h3>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {topExpenses.map((t, i) => (
                  <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "8px 0", borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                    <div>
                      <div style={{ fontSize: 13, fontWeight: 500, maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{t.description}</div>
                      <div style={{ fontSize: 11, color: "#6B7094" }}>{t.dateStr} · {t.category}</div>
                    </div>
                    <div style={{ fontFamily: "'Space Mono', monospace", fontWeight: 700, color: "#F97316", fontSize: 14 }}>
                      ₹{t.amount.toLocaleString("en-IN")}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Transactions */}
        {view === "transactions" && (
          <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 16, overflow: "hidden" }}>
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
                <thead>
                  <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.08)" }}>
                    {["Date", "Description", "Category", "Type", "Amount"].map(h => (
                      <th key={h} style={{ padding: "14px 18px", textAlign: "left", color: "#6B7094", fontWeight: 600, fontSize: 12, letterSpacing: "0.04em" }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {transactions.map((t, i) => (
                    <tr key={i} style={{ borderBottom: "1px solid rgba(255,255,255,0.03)" }}
                      onMouseEnter={e => e.currentTarget.style.background = "rgba(255,255,255,0.02)"}
                      onMouseLeave={e => e.currentTarget.style.background = "transparent"}>
                      <td style={{ padding: "12px 18px", color: "#8B8FA3", fontFamily: "'Space Mono', monospace", fontSize: 12 }}>{t.dateStr}</td>
                      <td style={{ padding: "12px 18px", fontWeight: 500, maxWidth: 260, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{t.description}</td>
                      <td style={{ padding: "12px 18px" }}>
                        <span style={{
                          background: `${CATEGORY_COLORS[t.category]}15`,
                          color: CATEGORY_COLORS[t.category],
                          padding: "4px 10px",
                          borderRadius: 6,
                          fontSize: 12,
                          fontWeight: 600
                        }}>{t.category}</span>
                      </td>
                      <td style={{ padding: "12px 18px" }}>
                        <span style={{ color: t.type === "income" ? "#22C55E" : "#F97316", fontSize: 12, fontWeight: 600, textTransform: "uppercase" }}>{t.type}</span>
                      </td>
                      <td style={{ padding: "12px 18px", fontFamily: "'Space Mono', monospace", fontWeight: 700, color: t.type === "income" ? "#22C55E" : "#F97316", textAlign: "right" }}>
                        {t.type === "income" ? "+" : "-"}₹{t.amount.toLocaleString("en-IN")}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
