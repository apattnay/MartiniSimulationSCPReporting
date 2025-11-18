
import plotly.graph_objects as go

# Data for SKU categories and their core count ranges
categories = ['LCC', 'HCC', 'XCC', 'UCC', 'AP', 'HD']
core_ranges = ['16–32', '48–64', '72–96', '96–128', '72–128', 'Up to 192']

# Assign numeric values for plotting (use upper bound for visualization)
core_values = [32, 64, 96, 128, 128, 192]

# Colors for each category
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

# Create bar chart
fig = go.Figure(data=[
    go.Bar(
        x=categories,
        y=core_values,
        text=core_ranges,
        textposition='outside',
        marker_color=colors
    )
])

# Update layout for clarity
fig.update_layout(
    title='Intel Xeon SKU Categories vs Core Count Ranges',
    xaxis_title='SKU Category',
    yaxis_title='Core Count (Upper Bound)',
    yaxis=dict(range=[0, 200]),
    template='plotly_white'
)

# Save the plot as JSON and PNG files
try:
    fig.write_json('output/xeon_sku_core_counts.json')
    fig.write_image('output/xeon_sku_core_counts.png')
    print('✅ Xeon SKU Core Count visualization saved successfully')
    print('📁 Files generated:')
    print('   - output/xeon_sku_core_counts.json')
    print('   - output/xeon_sku_core_counts.png')
except Exception as e:
    print(f'❌ Error saving visualization: {e}')
    print('💡 Make sure plotly-kaleido is installed: pip install plotly kaleido')

# Show the figure
fig.show()

import plotly.graph_objects as go

# Define the data for Intel Xeon families
xeon_families = [
    ["LCC (Low Core Count)", "Core Count-Based", "16–32", "150–225W", "8", "Entry-level servers, cost-sensitive"],
    ["HCC (High Core Count)", "Core Count-Based", "32–64", "300–350W", "8", "Balanced enterprise workloads"],
    ["XCC (Extreme Core Count)", "Core Count-Based", "64–96", "350–500W", "12", "HPC, virtualization, AI inference"],
    ["UCC (Ultra Core Count)", "Core Count-Based", "96–128", "500W", "12", "Flagship Granite Rapids for AI/HPC"],
    ["AP (Advanced Performance)", "Performance-Based", "72–128", "500–650W", "12–16", "HPC, AI training, liquid cooling"],
    ["SP (Scalable Performance)", "Performance-Based", "16–64", "150–350W", "8–12", "General-purpose enterprise workloads"],
    ["HD (High Density)", "Performance-Based", "Up to 192", "500W+", "16", "Telecom, hyperscale, high-density compute"],
    ["Suffix Variants (-N, -T, -M, -L, -V, -Y)", "Performance-Based", "Varies", "Varies", "Varies", "Network optimization, thermal tuning, large memory, VM density"],
    ["Sierra Forest", "Efficiency-Based", "Up to 288 E-cores", "Power-efficient", "12", "Cloud-native, scale-out workloads"],
    ["Clearwater Forest", "Efficiency-Based", "Up to 288 E-cores", "Power-efficient", "12", "Hyperscale, energy efficiency"],
    ["Xeon D-Series", "Specialized", "4–20", "Low-power", "4–6", "Edge computing, networking appliances"],
    ["Xeon E-Series", "Specialized", "4–8", "Low-power", "2–4", "Entry-level servers, workstations"],
    ["Xeon W-Series", "Specialized", "8–56", "150–350W", "4–8", "High-performance workstations"]
]

# Extract columns for the table
families = [row[0] for row in xeon_families]
classification = [row[1] for row in xeon_families]
core_range = [row[2] for row in xeon_families]
tdp = [row[3] for row in xeon_families]
memory_channels = [row[4] for row in xeon_families]
workloads = [row[5] for row in xeon_families]

# Define colors for classification
classification_colors = {
    "Core Count-Based": "lightblue",
    "Performance-Based": "lightgreen",
    "Efficiency-Based": "lightyellow",
    "Specialized": "lightpink"
}

row_colors = [classification_colors.get(cls, "white") for cls in classification]

# Create the Plotly table
fig = go.Figure(data=[go.Table(
    header=dict(values=["Family / Series", "Classification", "Core Range", "TDP", "Memory Channels", "Target Workloads"],
                fill_color="darkblue",
                font=dict(color="white", size=14),
                align="center"),
    cells=dict(values=[families, classification, core_range, tdp, memory_channels, workloads],
               fill_color=[row_colors],
               align="left",
               font=dict(size=12))
)])

# Update layout for better readability
fig.update_layout(
    title="Intel Xeon Families - Detailed Specifications",
    title_font_size=20,
    margin=dict(l=20, r=20, t=50, b=20)
)

# Save the visual matrix as JSON and PNG
fig.write_json("xeon_family_matrix.json")
fig.write_image("xeon_family_matrix.png")

print("Visual matrix table created and saved as 'xeon_family_matrix.json' and 'xeon_family_matrix.png'.")
fig.show()
