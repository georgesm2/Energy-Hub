<script>
  import LineChart from './LineChart.svelte';

  let { data } = $props();

  const PRICE_SCALE = 1000;
  const GEN_SCALE = 1000;

  function formatMoneyPerKWh(value) {
    if (!Number.isFinite(value)) return '—';
    return `£${(value / PRICE_SCALE).toPrecision(2)} / KWh`;
  }

  function formatTime(value) {
    return value ? value.substring(11, 16) : '—';
  }

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

  let dayGenData = $derived(
    asArray(data?.generation)
  );

  let priceSeries = $derived([
    {
      label: '',
      data: dayPriceData,
      xAccessor: (d) => new Date(d.startTime),
      yAccessor: (d) => d.price / PRICE_SCALE,
      stroke: '#ff0000'
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
      span: 12,
      title: 'Market Overview'
    },
    {
      kind: 'chart',
      span: 6,
      title: '£ UK Energy Market Index Price / KWh',
      series: priceSeries
    },
    {
      kind: 'chart',
      span: 6,
      title: 'UK Energy Generation by Type / GW',
      series: generationSeries
    }
  ]);
</script>

<div class="page-wrapper">
  <div class="dashboard-shell">
    <h1>UK Energy Dashboard</h1>
    <p>This project intends to bring all information on UK energy to one place</p>

    <div class="dashboard-grid">
      {#each dashboardSections as section, i}
        {#if section.kind === 'stats'}
          <aside class="card" style={`grid-column: span ${section.span};`}>
            <h3>{section.title}</h3>
            <p>Time: {data?.now ?? '—'}</p>
            <p>
              Price: {formatMoneyPerKWh(data?.price?.[0]?.price)} at {formatTime(data?.price?.[0]?.startTime)}
            </p>
          </aside>
        {:else if section.kind === 'chart'}
          <section class="card chart-block" style={`grid-column: span ${section.span};`}>
            <LineChart
              title={section.title}
              series={section.series}
            />
          </section>
        {/if}
      {/each}
    </div>
  </div>
</div>

<style>
  .page-wrapper {
    width: 100%;
    min-height: 100vh;
  }

  .dashboard-shell {
    width: 100%;
    max-width: 1500px; /* cap overall dashboard width to prevent cards from growing indefinitely */
    margin: 0 auto; /* center the capped container */
    /* padding-inline: clamp(16px, 3vw, 48px); */
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
    border-radius: 8px;
    padding: 16px;
    box-sizing: border-box;
    min-width: 0;
    display: flex;
    flex-direction: column;
    height: 100%; /* allow the card to stretch to the grid row height */
  }

  .chart-block {
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
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
</style>
