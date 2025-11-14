# CSV Download Feature - Trade History Export

## Overview
Added a feature to download all past trades as a CSV file for manual verification and analysis.

## How to Use

### From the Web Interface
1. Open the dashboard at `http://129.159.227.175:3000`
2. Look for the **Quick Actions** section in the right sidebar
3. Click the **"Download Trades CSV"** button (purple button with download icon)
4. The CSV file will be automatically downloaded to your computer

### From the API
You can also download the CSV directly via the API:
```bash
curl -o trades.csv http://129.159.227.175:8000/api/trades/download
```

## CSV File Contents

The downloaded CSV includes the following columns for each closed trade:

| Column | Description |
|--------|-------------|
| **Symbol** | Trading pair (e.g., SOL/USDT, LINK/USDT) |
| **Type** | Position type (long or short) |
| **Entry Price** | Price at which position was opened |
| **Exit Price** | Price at which position was closed |
| **Quantity** | Amount of crypto traded |
| **Leverage** | Leverage used (e.g., 2.0x for longs, 1.0x for shorts) |
| **Entry Time** | Timestamp when position opened |
| **Exit Time** | Timestamp when position closed |
| **Duration (hours)** | How long the position was held |
| **P&L ($)** | Profit/Loss in USD |
| **P&L (%)** | Profit/Loss as percentage |
| **Position Value** | Total position value (entry_price × quantity) |
| **Margin Used** | Actual margin/capital used (position_value ÷ leverage) |

## Sample CSV Output

```csv
Symbol,Type,Entry Price,Exit Price,Quantity,Leverage,Entry Time,Exit Time,Duration (hours),P&L ($),P&L (%),Position Value,Margin Used
SOL/USDT,long,167.13,166.79,14.958416,2.0,2025-11-10 12:08:33,2025-11-10 17:18:59,5.17,-10.17,-0.41,2500.0,1250.0
LINK/USDT,long,16.41,16.07,133.302864,2.0,2025-11-10 12:08:33,2025-11-10 17:18:59,5.17,-90.65,-4.14,2187.5,1093.75
```

## Verification Tips

### Calculate P&L Manually
For **Long positions**:
```
P&L = (Exit Price - Entry Price) × Quantity
```

For **Short positions**:
```
P&L = (Entry Price - Exit Price) × Quantity
```

### Verify Position Sizing
```
Position Value = Entry Price × Quantity
Margin Used = Position Value ÷ Leverage
```

For the SOL/USDT trade above:
- Position Value = 167.13 × 14.958416 = $2,500
- Margin Used = 2500 ÷ 2.0 = $1,250 ✓
- P&L = (166.79 - 167.13) × 14.958416 = -$10.17 ✓

### Check Total Returns
You can sum the P&L column to verify your total realized profit/loss matches the dashboard.

## File Naming
Files are automatically named with a timestamp:
```
trades_history_YYYYMMDD_HHMMSS.csv
```
Example: `trades_history_20251110_173000.csv`

## Notes
- Only **closed trades** are included in the export
- **Open positions** are not included (they don't have exit price/time yet)
- The file includes ALL historical trades since the bot started
- You can open the CSV in Excel, Google Sheets, or any spreadsheet software
- Perfect for tax reporting, performance analysis, and strategy verification

## API Endpoint
```
GET /api/trades/download
```

**Response**: CSV file download with `Content-Type: text/csv`

**Authentication**: None (currently - add authentication in production!)





