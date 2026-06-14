<script>
  import LineChart from './LineChart.svelte';

  let { data } = $props();



  function asArray(value) {
    return Array.isArray(value) ? value : [];
  }

  function quantityFor(entry, type) {
    const value = entry?.data?.find((item) => item.psrType === type)?.quantity;
    return Number.isFinite(value) ? value / GEN_SCALE : 0;
  }

  function sumQuantities(entry, types) {
    return types.reduce((sum, type) => sum + quantityFor(entry, type), 0);
  }

  let dayPriceData = $derived(
    data?.price ? [...data.price].reverse() : []
  );

  let dayAgileData = $derived(
    asArray(data.agile)
  );

  let dayGenData = $derived(
    asArray(data?.generation)
  );

  let priceSeries = $derived([
    {
      label: 'Wholesale Market Index',
      data: dayPriceData,
      xAccessor: (d) => new Date(d.startTime),
      yAccessor: (d) => d.price / PRICE_SCALE,
      stroke: '#ff0000'
    },
    {
      label: 'Octopus Agile',
      data: dayAgileData,
      xAccessor: (d) => new Date(d.valid_from),
      yAccessor: (d) => d.value_inc_vat / 100,
      stroke: '#0000ff'
    }
  ]);

  let generationSeries = $derived([
    {
      label: 'Solar',
      data: dayGenData,
      xAccessor: (d) => new Date(d.startTime),
      yAccessor: (d) => quantityFor(d, 'Solar'),
      stroke: '#ffec73'
    },
    {
      label: 'Nuclear',
      data: dayGenData,
      xAccessor: (d) => new Date(d.startTime),
      yAccessor: (d) => quantityFor(d, 'Nuclear'),
      stroke: '#0000ff'
    },
    {
      label: 'Gas',
      data: dayGenData,
      xAccessor: (d) => new Date(d.startTime),
      yAccessor: (d) => quantityFor(d, 'Fossil Gas'),
      stroke: '#ffa500'
    },
    {
      label: 'Wind',
      data: dayGenData,
      xAccessor: (d) => new Date(d.startTime),
      yAccessor: (d) => sumQuantities(d, ['Wind Offshore', 'Wind Onshore']),
      stroke: '#008000'
    },
    {
      label: 'Biomass',
      data: dayGenData,
      xAccessor: (d) => new Date(d.startTime),
      yAccessor: (d) => quantityFor(d, 'Biomass'),
      stroke: '#800080'
    },
    {
      label: 'Coal',
      data: dayGenData,
      xAccessor: (d) => new Date(d.startTime),
      yAccessor: (d) => quantityFor(d, 'Fossil Hard Coal'),
      stroke: '#555555'
    }
  ]);

  // Define your dashboard in one place.
  // `span` uses a 12-column grid.
  // 12 = full width, 6 = half width, 3 = quarter width, etc.
  let dashboardSections = $derived([
    {
      kind: 'stats',
      span: 3,
      title: 'Market Overview'
    },
    {
      kind: 'hist-buttons',
      span: 5,
      title: 'Historical Data'
    },
    {
      kind: 'future-buttons',
      span: 4,
      title: 'Forecast'
    },
    {
      kind: 'chart',
      span: 6,
      title: '£ UK Electricity Market Index Price / KWh',
      series: priceSeries,
      info: 'Note: Agile price forecasts ahead of public release of wholesale market index.'
    },
    {
      kind: 'chart',
      span: 6,
      title: 'UK Electricity Generation by Type / GW',
      series: generationSeries
    }
  ]);
</script>

<!-- <div class="page-wrapper">
  <div class="dashboard-shell">
    <p>This project intends to bring all information on UK energy to one place</p>

    <div class="dashboard-grid">
      {#each dashboardSections as section, i}
        {#if section.kind === 'stats'}
          <aside class="card" style={`grid-column: span ${section.span};`}>
            <h3>{section.title}</h3>
            <p>Time: {data?.now ?? '—'}</p>
            <p>Demand: {data?.demand?.[0]?.quantity / 1000} GW at {formatTime(data?.demand?.[0]?.publishTime)}</p>
            <p>
              Price: {formatMoneyPerKWh(data?.price?.[0]?.price)} at {formatTime(data?.price?.[0]?.startTime)}
            </p>
          </aside>
        {:else if section.kind === 'hist-buttons'}
          <section class="card" style={`grid-column: span ${section.span};`}>
            <h3>{section.title}</h3>
            <button>Today</button>
            <button>Last Week</button>
            <button>Last Month</button>
            <button>Last Year</button>
            <button>All Time</button>
          </section>
        {:else if section.kind === 'future-buttons'}
          <section class="card" style={`grid-column: span ${section.span};`}>
            <h3>{section.title}</h3>
            <button>Today</button>
            <button>Tomorrow</button>
            <button>This Week</button>
          </section>
        {:else if section.kind === 'chart'}
          <section class="card chart-block" style={`grid-column: span ${section.span};`}>
            <LineChart
              title={section.title}
              series={section.series}
            />
            <p>{section.info}</p>
          </section>
        {/if}
      {/each}
    </div>
  </div>
</div> -->

<main class="dashboard-container">
    <h1>UK Energy Hub Metrics</h1>
    <p>Displaying the latest {data.metrics.length} data points extracted from Cloudflare D1.</p>

    <div class="table-wrapper">
        <table>
            <thead>
                <tr>
                    <th>Timestamp (UTC)</th>
                    <th>Category Stream</th>
                    <th>Recorded Value</th>
                </tr>
            </thead>
            <tbody>
                {#each data.metrics as metric}
                    <tr>
                        <td>{metric.timestamp}</td>
                        <td class="badge">{metric.category}</td>
                        <td>{metric.value.toFixed(4)}</td>
                    </tr>
                {:else}
                    <tr>
                        <td colspan="3">No historical data streamed yet.</td>
                    </tr>
                {/each}
            </tbody>
        </table>
    </div>
</main>

<style>
  .page-wrapper {
    width: 100%;
    min-height: 100vh;
  }

  .dashboard-shell {
    width: 100%;
    max-width: 1200px; /* cap overall dashboard width to prevent cards from growing indefinitely */
    margin: 0 auto; /* center the capped container */
    box-sizing: border-box;
    padding-top: 0px;
    padding-left: 1em;
    padding-right: 1em;
  }

  .dashboard-grid {
    display: grid;
    grid-template-columns: repeat(12, minmax(0, 1fr));
    gap: 5px;
    width: 100%;
    box-sizing: border-box;
    align-items: stretch; /* ensure children in the same row match height */
  }

  .card {
    background: #ffffff;
    border: 2px solid #e0e0e0;
    border-radius: 25px;
    padding: 16px;
    box-sizing: border-box;
    min-width: 0;
    height: 100%; /* allow the card to stretch to the grid row height */

    h3 {
      margin: 0 0 8px 0;
    }

    p {
      margin: 0;
    }
  }

  .chart-block {
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    height: 100%;
    min-height: 500px;
  }

  .chart-block :global(> :first-child) {
    flex-grow: 1;
    /* If LineChart relies on a percentage height internally, 
       min-height ensures it computes correctly */
  }

  @media (max-width: 1024px) {
    .dashboard-grid {
      grid-template-columns: repeat(12, minmax(0, 1fr));
    }
  }

  @media (max-width: 800px) {
    .dashboard-grid {
      grid-template-columns: 1fr;
    }

    .dashboard-grid > * {
      grid-column: auto !important;
    }
    /* Reduce the outer padding on small screens to maximize usable space */
    .dashboard-shell {
      padding-inline: 8px;
    }
  }

      .dashboard-container { padding: 2rem; font-family: sans-serif; }
    .table-wrapper { margin-top: 1.5rem; overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; text-align: left; }
    th, td { padding: 0.75rem; border-bottom: 1px solid #ddd; }
    th { background-color: #f4f4f4; }
    .badge { font-weight: bold; color: #2563eb; }
</style>

