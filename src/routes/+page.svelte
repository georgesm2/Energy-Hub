<h1>Welcome to Energy Hub</h1>
<p>This project intends to bring all information on UK energy to one place</p>

<p>Time: {data.now}</p>
<p>Price: £{data.price[0].price} / MWh (at {data.price[0].startTime.substring(11,16)})</p>

<div class="wrapper" bind:clientWidth={width}>
  {#if data && width && xScale && yScale && lineGenerator}
    <svg {width} {height}>
      <AxisBottom
        {width}
        {height}
        {margin}
        tick_number={width > 380 ? 10 : 4}
        {xScale}
        format={scaleTime().tickFormat(2, "%H:%M")} />
      <AxisLeft {width} {height} {margin} {yScale} position="left" />
      <Labels
        labelfory={true}
        {width}
        {height}
        {margin}
        yoffset={10}
        xoffset={350}
        label={'£ UK Energy Market Index Price / MWh ↑'} />

      <path
        in:draw={{ duration: 3000 }}
        d={lineGenerator(dayPriceData)}
        stroke="#ff0000"
        stroke-width={2.5}
        fill="none" />
    </svg>
  {/if}
</div>

<script>
import {scaleTime, scaleLinear } from 'd3-scale';
import { extent, max } from 'd3-array';
import { line, curveBasis } from 'd3-shape';
import { draw } from 'svelte/transition';
import { onMount } from 'svelte';
// Component imports
import AxisLeft from './AxisLeftV5.svelte';
import AxisBottom from './AxisBottomV5.svelte';
import Labels from './Labels.svelte';

let { data } = $props();
let dayPriceData = $derived(data?.price.reverse() || []);

let width = $state(0);
const height = 350;
const margin = {top: 60, right: 35, bottom: 30, left:35};

let xScale = $derived(
dayPriceData && width
    ? scaleTime()
        .domain(extent(dayPriceData, (d) => new Date(d.startTime)))
        .range([margin.left, width - margin.right])
    : null
);

let yScale = $derived(
dayPriceData && width
    ? scaleLinear()
        .domain([0, max(dayPriceData, (d) => d.price)])
        .range([height - margin.bottom, margin.top])
    : null
);

let lineGenerator = $derived(
xScale && yScale
    ? line()
        .x((d) => xScale(new Date(d.startTime)))
        .y((d) => yScale(d.price))
        .curve(curveBasis)
    : null
);

</script>