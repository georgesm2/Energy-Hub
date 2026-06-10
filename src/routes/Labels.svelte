<script>
  // Declare props using $props
  let {
    width,
    height,
    margin,
    label,
    yoffset = 0,
    xoffset = 0,
    labelforx = false,
    labelfory = false,
    textanchor = 'end',
    fillColor = 'black'
  } = $props();
</script>

{#if width}
  <g class="labels-x-y text-sm">
    {#if labelforx}
      <text
        fill={fillColor}
        x={+margin.left + width - 66 + xoffset}
        y={+height + margin.top - 40 + yoffset}
        text-anchor={textanchor}>
        {label}
      </text>
    {/if}
    {#if labelfory}
      <text
        fill={fillColor}
        x={+margin.left + xoffset}
        y={-margin.top + 80 + yoffset}
        text-anchor={textanchor}>
        {label}
      </text>
    {/if}
  </g>
{/if}