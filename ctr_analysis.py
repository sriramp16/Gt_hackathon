import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Load datasets
train = pd.read_csv('train_adc/train.csv')
item_data = pd.read_csv('train_adc/item_data.csv')

print("="*80)
print("CTR TEST DATASET - COMPREHENSIVE ANALYSIS")
print("="*80)

# ============================================================================
# 1. DATA OVERVIEW
# ============================================================================
print("\n" + "="*80)
print("1. DATA OVERVIEW")
print("="*80)
print(f"\nTrain Dataset Shape: {train.shape}")
print(f"Item Data Shape: {item_data.shape}")
print(f"\nTrain Columns: {train.columns.tolist()}")
print(f"Item Data Columns: {item_data.columns.tolist()}")
print(f"\nTrain Dataset Info:")
print(train.info())
print(f"\nFirst 20 rows of Train data:")
print(train.head(20))

# ============================================================================
# 2. DATA CLEANING ASSESSMENT
# ============================================================================
print("\n" + "="*80)
print("2. DATA CLEANING ASSESSMENT")
print("="*80)

print("\n--- Missing Values ---")
print("Train data missing values:")
print(train.isnull().sum())
print("\nItem data missing values:")
print(item_data.isnull().sum())

print("\n--- Duplicates ---")
print(f"Train duplicates: {train.duplicated().sum()}")
print(f"Item data duplicates: {item_data.duplicated().sum()}")
print(f"Train duplicates (by impression_id): {train.duplicated(subset=['impression_id']).sum()}")

print("\n--- Data Types ---")
print("Train dtypes:")
print(train.dtypes)

print("\n--- Abnormal Entries ---")
print(f"Unique values in 'is_click': {train['is_click'].unique()}")
print(f"Unique values in 'is_4G': {train['is_4G'].unique()}")
print(f"Unique OS versions: {train['os_version'].unique()}")
print(f"Date range: {train['impression_time'].min()} to {train['impression_time'].max()}")

# ============================================================================
# 3. AGGREGATE METRICS (CTR, CPM, etc.)
# ============================================================================
print("\n" + "="*80)
print("3. KPI CALCULATION & AGGREGATION")
print("="*80)

# Group by app_code to calculate CTR and other metrics
app_metrics = train.groupby('app_code').agg(
    impressions=('impression_id', 'count'),
    clicks=('is_click', 'sum'),
).reset_index()

app_metrics['ctr'] = (app_metrics['clicks'] / app_metrics['impressions'] * 100).round(4)
app_metrics = app_metrics.sort_values('ctr', ascending=False)

print("\n--- Overall Campaign Metrics ---")
total_impressions = train.shape[0]
total_clicks = train['is_click'].sum()
overall_ctr = (total_clicks / total_impressions * 100)

print(f"Total Impressions: {total_impressions:,}")
print(f"Total Clicks: {total_clicks:,}")
print(f"Overall CTR: {overall_ctr:.4f}%")
print(f"\n--- By App Code ---")
print(app_metrics.to_string(index=False))

# ============================================================================
# 4. EXPLORATORY DATA ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("4. EXPLORATORY DATA ANALYSIS")
print("="*80)

print("\n--- Summary Statistics ---")
print(f"Mean CTR: {app_metrics['ctr'].mean():.4f}%")
print(f"Median CTR: {app_metrics['ctr'].median():.4f}%")
print(f"Std Dev CTR: {app_metrics['ctr'].std():.4f}%")
print(f"Min CTR: {app_metrics['ctr'].min():.4f}%")
print(f"Max CTR: {app_metrics['ctr'].max():.4f}%")

print(f"\nMean Impressions per App: {app_metrics['impressions'].mean():.0f}")
print(f"Median Impressions per App: {app_metrics['impressions'].median():.0f}")
print(f"Mean Clicks per App: {app_metrics['clicks'].mean():.0f}")

# ============================================================================
# 5. TOP & BOTTOM PERFORMERS
# ============================================================================
print("\n" + "="*80)
print("5. TOP & BOTTOM PERFORMERS")
print("="*80)

print("\n--- Top 10 Apps by CTR ---")
top_10 = app_metrics.nlargest(10, 'ctr')[['app_code', 'impressions', 'clicks', 'ctr']]
print(top_10.to_string(index=False))

print("\n--- Bottom 10 Apps by CTR ---")
bottom_10 = app_metrics.nsmallest(10, 'ctr')[['app_code', 'impressions', 'clicks', 'ctr']]
print(bottom_10.to_string(index=False))

# ============================================================================
# 6. OUTLIER DETECTION
# ============================================================================
print("\n" + "="*80)
print("6. OUTLIER DETECTION")
print("="*80)

Q1_ctr = app_metrics['ctr'].quantile(0.25)
Q3_ctr = app_metrics['ctr'].quantile(0.75)
IQR_ctr = Q3_ctr - Q1_ctr
lower_bound = Q1_ctr - 1.5 * IQR_ctr
upper_bound = Q3_ctr + 1.5 * IQR_ctr

outliers = app_metrics[(app_metrics['ctr'] < lower_bound) | (app_metrics['ctr'] > upper_bound)]
print(f"CTR IQR Range: {Q1_ctr:.4f}% - {Q3_ctr:.4f}%")
print(f"Outlier Bounds: {lower_bound:.4f}% - {upper_bound:.4f}%")
print(f"Number of Outliers: {len(outliers)}")
print(f"\n--- High CTR Outliers (Unusually Good) ---")
high_outliers = outliers[outliers['ctr'] > upper_bound].sort_values('ctr', ascending=False)
if len(high_outliers) > 0:
    print(high_outliers[['app_code', 'impressions', 'clicks', 'ctr']].head(10).to_string(index=False))
else:
    print("None")

print(f"\n--- Low CTR Outliers (Unusually Bad) ---")
low_outliers = outliers[outliers['ctr'] < lower_bound].sort_values('ctr', ascending=True)
if len(low_outliers) > 0:
    print(low_outliers[['app_code', 'impressions', 'clicks', 'ctr']].head(10).to_string(index=False))
else:
    print("None")

# ============================================================================
# 7. FEATURE ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("7. FEATURE ANALYSIS")
print("="*80)

print("\n--- CTR by OS Version ---")
os_metrics = train.groupby('os_version').agg(
    impressions=('impression_id', 'count'),
    clicks=('is_click', 'sum'),
).reset_index()
os_metrics['ctr'] = (os_metrics['clicks'] / os_metrics['impressions'] * 100).round(4)
os_metrics = os_metrics.sort_values('ctr', ascending=False)
print(os_metrics.to_string(index=False))

print("\n--- CTR by 4G Status ---")
g4_metrics = train.groupby('is_4G').agg(
    impressions=('impression_id', 'count'),
    clicks=('is_click', 'sum'),
).reset_index()
g4_metrics['4G_Status'] = g4_metrics['is_4G'].map({0: 'No 4G', 1: '4G'})
g4_metrics['ctr'] = (g4_metrics['clicks'] / g4_metrics['impressions'] * 100).round(4)
print(g4_metrics[['4G_Status', 'impressions', 'clicks', 'ctr']].to_string(index=False))

# ============================================================================
# 8. ANOMALIES & SUSPICIOUS PATTERNS
# ============================================================================
print("\n" + "="*80)
print("8. ANOMALIES & SUSPICIOUS PATTERNS")
print("="*80)

# Apps with 0 clicks
zero_click_apps = app_metrics[app_metrics['clicks'] == 0]
print(f"\n--- Apps with Zero Clicks: {len(zero_click_apps)} ---")
print(f"Impressions wasted on zero-click apps: {zero_click_apps['impressions'].sum():,}")

# Apps with very low impression count
low_impression_apps = app_metrics[app_metrics['impressions'] < 10]
print(f"\n--- Apps with <10 Impressions: {len(low_impression_apps)} ---")
print(f"Total impressions in low-volume apps: {low_impression_apps['impressions'].sum():,}")

# Click spikes
print(f"\n--- Impression Distribution ---")
print(f"Apps with <100 impressions: {len(app_metrics[app_metrics['impressions'] < 100])}")
print(f"Apps with 100-1000 impressions: {len(app_metrics[(app_metrics['impressions'] >= 100) & (app_metrics['impressions'] < 1000)])}")
print(f"Apps with >1000 impressions: {len(app_metrics[app_metrics['impressions'] >= 1000])}")

# ============================================================================
# 9. SAVE KEY METRICS FOR REPORT
# ============================================================================
print("\n" + "="*80)
print("9. SAVING ANALYSIS RESULTS")
print("="*80)

# Save top and bottom performers
app_metrics.to_csv('app_metrics.csv', index=False)
print("✓ Saved: app_metrics.csv")

# Create summary statistics file
summary_stats = {
    'Metric': ['Total Impressions', 'Total Clicks', 'Overall CTR (%)', 'Mean App CTR (%)', 
               'Median App CTR (%)', 'Std Dev CTR (%)', 'Min CTR (%)', 'Max CTR (%)',
               'Total Apps', 'Zero-Click Apps', 'Low-Volume Apps (<10 imp)'],
    'Value': [
        f"{total_impressions:,}",
        f"{total_clicks:,}",
        f"{overall_ctr:.4f}",
        f"{app_metrics['ctr'].mean():.4f}",
        f"{app_metrics['ctr'].median():.4f}",
        f"{app_metrics['ctr'].std():.4f}",
        f"{app_metrics['ctr'].min():.4f}",
        f"{app_metrics['ctr'].max():.4f}",
        f"{len(app_metrics)}",
        f"{len(zero_click_apps)}",
        f"{len(low_impression_apps)}"
    ]
}
summary_df = pd.DataFrame(summary_stats)
summary_df.to_csv('summary_statistics.csv', index=False)
print("✓ Saved: summary_statistics.csv")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
