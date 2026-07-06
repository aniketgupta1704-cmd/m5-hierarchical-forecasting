"""Static SVG diagrams for the dashboard (embedded via st.components)."""

HIERARCHY_SVG = """
<svg width="100%" viewBox="0 0 680 470" preserveAspectRatio="xMidYMid meet"
     style="max-width:680px;height:auto;display:block;margin:0 auto"
     xmlns="http://www.w3.org/2000/svg"
     font-family="-apple-system, Segoe UI, Arial, sans-serif">
  <defs>
    <marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="#888" stroke-width="1.5"
            stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>

  <line x1="340" y1="86"  x2="340" y2="110" stroke="#888" stroke-width="1.5" marker-end="url(#ar)"/>
  <line x1="340" y1="166" x2="340" y2="190" stroke="#888" stroke-width="1.5" marker-end="url(#ar)"/>
  <line x1="340" y1="246" x2="340" y2="270" stroke="#888" stroke-width="1.5" marker-end="url(#ar)"/>
  <line x1="340" y1="326" x2="340" y2="350" stroke="#888" stroke-width="1.5" marker-end="url(#ar)"/>

  <g>
    <rect x="250" y="42" width="180" height="44" rx="8" fill="#F1EFE8" stroke="#5F5E5A" stroke-width="0.5"/>
    <text x="340" y="60" text-anchor="middle" font-size="14" font-weight="500" fill="#2C2C2A">Total (national)</text>
    <text x="340" y="76" text-anchor="middle" font-size="12" fill="#5F5E5A">1 series</text>
  </g>
  <g>
    <rect x="240" y="122" width="200" height="44" rx="8" fill="#F1EFE8" stroke="#5F5E5A" stroke-width="0.5"/>
    <text x="340" y="140" text-anchor="middle" font-size="14" font-weight="500" fill="#2C2C2A">State</text>
    <text x="340" y="156" text-anchor="middle" font-size="12" fill="#5F5E5A">3 series</text>
  </g>
  <g>
    <rect x="230" y="202" width="220" height="44" rx="8" fill="#F1EFE8" stroke="#5F5E5A" stroke-width="0.5"/>
    <text x="340" y="220" text-anchor="middle" font-size="14" font-weight="500" fill="#2C2C2A">Store</text>
    <text x="340" y="236" text-anchor="middle" font-size="12" fill="#5F5E5A">10 series</text>
  </g>
  <g>
    <rect x="210" y="282" width="260" height="44" rx="8" fill="#E1F5EE" stroke="#0F6E56" stroke-width="1"/>
    <text x="340" y="300" text-anchor="middle" font-size="14" font-weight="500" fill="#085041">Store x category</text>
    <text x="340" y="316" text-anchor="middle" font-size="12" fill="#0F6E56">30 series</text>
  </g>
  <g>
    <rect x="190" y="362" width="300" height="44" rx="8" fill="#E6F1FB" stroke="#185FA5" stroke-width="1"/>
    <text x="340" y="380" text-anchor="middle" font-size="14" font-weight="500" fill="#0C447C">Item x store (leaves)</text>
    <text x="340" y="396" text-anchor="middle" font-size="12" fill="#185FA5">30,490 series</text>
  </g>

  <g>
    <rect x="500" y="282" width="150" height="44" rx="8" fill="#E1F5EE" stroke="#0F6E56" stroke-width="0.5"/>
    <text x="575" y="300" text-anchor="middle" font-size="14" font-weight="500" fill="#085041">Prophet</text>
    <text x="575" y="316" text-anchor="middle" font-size="12" fill="#0F6E56">fits here</text>
  </g>
  <line x1="470" y1="304" x2="498" y2="304" stroke="#888" stroke-width="1.5" marker-end="url(#ar)"/>

  <g>
    <rect x="500" y="362" width="150" height="44" rx="8" fill="#E6F1FB" stroke="#185FA5" stroke-width="0.5"/>
    <text x="575" y="380" text-anchor="middle" font-size="14" font-weight="500" fill="#0C447C">LightGBM</text>
    <text x="575" y="396" text-anchor="middle" font-size="12" fill="#185FA5">fits here</text>
  </g>
  <line x1="490" y1="384" x2="498" y2="384" stroke="#888" stroke-width="1.5" marker-end="url(#ar)"/>

  <g>
    <rect x="40" y="122" width="120" height="284" rx="12" fill="#FAECE7" stroke="#993C1D" stroke-width="0.5"/>
    <text x="100" y="256" text-anchor="middle" font-size="14" font-weight="500" fill="#712B13">MinT</text>
    <text x="100" y="274" text-anchor="middle" font-size="12" fill="#993C1D">reconciles</text>
    <text x="100" y="290" text-anchor="middle" font-size="12" fill="#993C1D">all levels</text>
  </g>
  <line x1="160" y1="144" x2="238" y2="144" stroke="#B4B2A9" stroke-width="0.5" stroke-dasharray="3 3"/>
  <line x1="160" y1="224" x2="228" y2="224" stroke="#B4B2A9" stroke-width="0.5" stroke-dasharray="3 3"/>
  <line x1="160" y1="304" x2="208" y2="304" stroke="#B4B2A9" stroke-width="0.5" stroke-dasharray="3 3"/>
  <line x1="160" y1="384" x2="188" y2="384" stroke="#B4B2A9" stroke-width="0.5" stroke-dasharray="3 3"/>

  <text x="340" y="440" text-anchor="middle" font-size="12" fill="#5F5E5A">Forecasts sum up the pyramid; reconciliation keeps every level consistent</text>
</svg>
"""


PIPELINE_SVG = """
<svg width="100%" viewBox="0 0 680 300" preserveAspectRatio="xMidYMid meet"
     style="max-width:680px;height:auto;display:block;margin:0 auto"
     xmlns="http://www.w3.org/2000/svg"
     font-family="-apple-system, Segoe UI, Arial, sans-serif">
  <defs>
    <marker id="pa" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="#888" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>
  <g>
    <rect x="40" y="50" width="180" height="52" rx="8" fill="#F1EFE8" stroke="#5F5E5A" stroke-width="0.5"/>
    <text x="130" y="72" text-anchor="middle" font-size="14" font-weight="500" fill="#2C2C2A">1 - Hierarchical EDA</text>
    <text x="130" y="90" text-anchor="middle" font-size="12" fill="#5F5E5A">intermittency, seasonality</text>
  </g>
  <line x1="220" y1="76" x2="252" y2="76" stroke="#888" stroke-width="1.5" marker-end="url(#pa)"/>
  <g>
    <rect x="254" y="50" width="180" height="52" rx="8" fill="#F1EFE8" stroke="#5F5E5A" stroke-width="0.5"/>
    <text x="344" y="72" text-anchor="middle" font-size="14" font-weight="500" fill="#2C2C2A">2 - Feature engineering</text>
    <text x="344" y="90" text-anchor="middle" font-size="12" fill="#5F5E5A">lags, rolling, calendar</text>
  </g>
  <line x1="434" y1="76" x2="466" y2="76" stroke="#888" stroke-width="1.5" marker-end="url(#pa)"/>
  <g>
    <rect x="468" y="50" width="180" height="52" rx="8" fill="#E6F1FB" stroke="#185FA5" stroke-width="1"/>
    <text x="558" y="72" text-anchor="middle" font-size="14" font-weight="500" fill="#0C447C">3 - Four models</text>
    <text x="558" y="90" text-anchor="middle" font-size="11" fill="#185FA5">naive/Prophet/LGB/N-BEATS</text>
  </g>
  <line x1="558" y1="102" x2="558" y2="128" stroke="#888" stroke-width="1.5" marker-end="url(#pa)"/>
  <g>
    <rect x="468" y="130" width="180" height="52" rx="8" fill="#E1F5EE" stroke="#0F6E56" stroke-width="1"/>
    <text x="558" y="152" text-anchor="middle" font-size="14" font-weight="500" fill="#085041">4 - Reconciliation</text>
    <text x="558" y="170" text-anchor="middle" font-size="12" fill="#0F6E56">block-wise MinT</text>
  </g>
  <line x1="466" y1="156" x2="434" y2="156" stroke="#888" stroke-width="1.5" marker-end="url(#pa)"/>
  <g>
    <rect x="254" y="130" width="180" height="52" rx="8" fill="#E1F5EE" stroke="#0F6E56" stroke-width="0.5"/>
    <text x="344" y="152" text-anchor="middle" font-size="14" font-weight="500" fill="#085041">5 - WRMSSE eval</text>
    <text x="344" y="170" text-anchor="middle" font-size="12" fill="#0F6E56">calibration, backtest</text>
  </g>
  <line x1="252" y1="156" x2="220" y2="156" stroke="#888" stroke-width="1.5" marker-end="url(#pa)"/>
  <g>
    <rect x="40" y="130" width="180" height="52" rx="8" fill="#FAECE7" stroke="#993C1D" stroke-width="1"/>
    <text x="130" y="152" text-anchor="middle" font-size="14" font-weight="500" fill="#712B13">6 - Business layer</text>
    <text x="130" y="170" text-anchor="middle" font-size="11" fill="#993C1D">newsvendor, cost-of-error</text>
  </g>
  <line x1="130" y1="182" x2="130" y2="208" stroke="#888" stroke-width="1.5" marker-end="url(#pa)"/>
  <g>
    <rect x="40" y="210" width="180" height="52" rx="8" fill="#EEEDFE" stroke="#534AB7" stroke-width="1"/>
    <text x="130" y="232" text-anchor="middle" font-size="14" font-weight="500" fill="#3C3489">7 - Streamlit dashboard</text>
    <text x="130" y="250" text-anchor="middle" font-size="12" fill="#534AB7">4 pages, live calculator</text>
  </g>
</svg>
"""

MODEL_WINS_SVG = """
<svg width="100%" viewBox="0 0 680 210" preserveAspectRatio="xMidYMid meet"
     style="max-width:680px;height:auto;display:block;margin:0 auto"
     xmlns="http://www.w3.org/2000/svg"
     font-family="-apple-system, Segoe UI, Arial, sans-serif">
  <g>
    <rect x="40" y="40" width="600" height="60" rx="10" fill="#E1F5EE" stroke="#0F6E56" stroke-width="1"/>
    <text x="64" y="64" font-size="14" font-weight="500" fill="#085041">Aggregate levels (national, state, store, store x category)</text>
    <text x="64" y="86" font-size="12" fill="#0F6E56">Prophet wins - fits the smooth aggregate directly (RMSE 210 vs 500 for summed leaves)</text>
  </g>
  <g>
    <rect x="40" y="120" width="600" height="60" rx="10" fill="#E6F1FB" stroke="#185FA5" stroke-width="1"/>
    <text x="64" y="144" font-size="14" font-weight="500" fill="#0C447C">Leaf level (30,490 item x store series)</text>
    <text x="64" y="166" font-size="12" fill="#185FA5">LightGBM wins - handles intermittency (WRMSSE 0.84, beats deep N-BEATS 0.88)</text>
  </g>
</svg>
"""