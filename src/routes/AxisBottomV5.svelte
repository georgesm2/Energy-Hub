<script>
  // Props
  let {
    xScale,
    margin,
    height,
    width,
    ticksNumber = 6,
    format = null
  } = $props();

  let dynamicTicksNumber = $derived(
    width ? Math.max(2, Math.floor(width / 80)) : ticksNumber
  );

  let ticks = $derived(
    xScale ? xScale.ticks(dynamicTicksNumber) : []
  );

  // Conditionally apply the formatter if provided
  const formatter = format
    ? (tick) => format(tick) // Use the provided formatter
    : (tick) => tick; // Default: no formatting
</script>

{#if xScale}
  <g transform="translate(0,{height - margin.bottom})">
    <line stroke="currentColor" x1={margin.left} x2={width - margin.right} />

    {#each ticks as tick}
      <g transform="translate({xScale(tick)}, 0)">
        <line
          stroke="currentColor"
          x1={0}
          x2={0}
          y1={0}
          y2={6} />
        
        <text
          font-size="12px"
          fill="currentColor"
          text-anchor="middle"
          x={0}
          y={20}>
          {formatter(tick)}
        </text>
      </g>
    {/each}
  </g>
{/if}