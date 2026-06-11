<script>
  import { scaleTime, scaleLinear } from 'd3-scale';
  import { extent, max, min } from 'd3-array';
  import { line, curveBasis } from 'd3-shape';

  import AxisLeft from './AxisLeftV5.svelte';
  import AxisBottom from './AxisBottomV5.svelte';

  let {
    title,
    series = [],
    margin = { top: 10, right: 40, bottom: 30, left: 40 },
    xFormat = (d) => String(d.getHours()).padStart(2, '0') + ':00',
    curve = curveBasis
  } = $props();

  let width = $state(0);
  
  // 1. We track the explicit height of the SVG container, not the whole card
  let svgHeight = $state(0); 

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
  
  // 2. Base your yScale calculation strictly on the svgHeight!
  let yScale = $derived(
    allPoints.length && width && svgHeight
      ? scaleLinear()
          .domain([
            Math.min(0, min(series, (s) => min(s.data ?? [], s.yAccessor))),
            max(series, (s) => max(s.data ?? [], s.yAccessor))
          ])
          .nice()
          .range([svgHeight - margin.bottom, margin.top]) // Use svgHeight here
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
    <h3 class="chart-title">{title}</h3>
  {/if}

  <svg width="100%" class="fluid-svg" bind:clientHeight={svgHeight}>
    {#if width && svgHeight && xScale && yScale}
      <AxisBottom
        {width}
        height={svgHeight}  {margin}
        {xScale}
        format={xFormat}
      />

      <AxisLeft
        {width}
        height={svgHeight}  {margin}
        {yScale}
        position="left"
      />

      {#each series as s}
        {#if s.data?.length}
          {#key s.data}
            <path
              d={makeLineGenerator(s)(s.data)}
              stroke={s.stroke ?? '#000000'}
              stroke-width={s.strokeWidth ?? 2}
              fill="none"
            />
          {/key}
        {/if}
      {/each}
    {/if}
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
</div>

<style>
  .chart-wrapper {
    width: 100%;
    height: 100%;
    min-width: 0;
    display: flex;
    flex-direction: column;
    flex-grow: 1;
  }

  h3 {
    margin: 0 0 8px 0;
  }

  svg {
    display: block;
    flex-grow:1 ;
  }

  .legend {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 8px;
    font-size: 0.875rem;
    flex-shrink: 0;
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .legend-line {
    width: 24px;
    height: 4px;
    display: inline-block;
    border-radius: 999px;
  }
</style>