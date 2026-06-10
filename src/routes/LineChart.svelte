<script>
  import { scaleTime, scaleLinear } from 'd3-scale';
  import { extent, max, min } from 'd3-array';
  import { line, curveBasis } from 'd3-shape';
  import { draw } from 'svelte/transition';

  import AxisLeft from './AxisLeftV5.svelte';
  import AxisBottom from './AxisBottomV5.svelte';

  let {
    title,
    series = [],
    height = 350,
    margin = { top: 10, right: 35, bottom: 30, left: 30 },
    xFormat = (d) => String(d.getHours()).padStart(2, '0') + ':00',
    curve = curveBasis
  } = $props();

  let width = $state(0);

  let allPoints = $derived(
    series.flatMap((s) => s.data ?? [])
  );

  let xScale = $derived(
    allPoints.length && width
      ? scaleTime()
          .domain([
            min(series, (s) => min(s.data ?? [], s.xAccessor)),
            max(series, (s) => max(s.data ?? [], s.xAccessor))
          ])
          .range([margin.left, width - margin.right])
      : null
  );
  let yScale = $derived(
    allPoints.length && width
      ? scaleLinear()
          .domain([
            min(series, (s) => min(s.data ?? [], s.yAccessor)),
            max(series, (s) => max(s.data ?? [], s.yAccessor))
          ])
          .nice()
          .range([height - margin.bottom, margin.top])
      : null
  );

  function makeLineGenerator(s) {
    return line()
      .x((d) => xScale(s.xAccessor(d)))
      .y((d) => yScale(s.yAccessor(d)))
      .curve(curve);
  }
</script>

<div class="chart-wrapper" bind:clientWidth={width}>
  {#if title}
    <h3>{title}</h3>
  {/if}

  {#if width && xScale && yScale}
    <svg {width} {height}>
      <AxisBottom
        {width}
        {height}
        {margin}
        {xScale}
        format={xFormat}
      />

      <AxisLeft
        {width}
        {height}
        {margin}
        {yScale}
        position="left"
      />

      {#each series as s}
        {#if s.data?.length}
          <path
            in:draw={{ duration: 10000 }}
            d={makeLineGenerator(s)(s.data)}
            stroke={s.stroke ?? '#000000'}
            stroke-width={s.strokeWidth ?? 2}
            fill="none"
          />
        {/if}
      {/each}
    </svg>

    {#if series.some((s) => s.label)}
      <div class="legend">
        {#each series as s}
          {#if s.label}
            <div class="legend-item">
              <span
                class="legend-line"
                style={`background-color: ${s.stroke ?? '#000000'}`}
              ></span>
              <span>{s.label}</span>
            </div>
          {/if}
        {/each}
      </div>
    {/if}
  {/if}
</div>

<style>
  .chart-wrapper {
    width: 100%;
    min-width: 0;
  }

  h3 {
    margin: 0 0 8px 0;
  }

  svg {
    display: block;
  }

  .legend {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 8px;
    font-size: 0.875rem;
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .legend-line {
    width: 24px;
    height: 3px;
    display: inline-block;
    border-radius: 999px;
  }
</style>