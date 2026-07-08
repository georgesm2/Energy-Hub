<script>
    import { Chart } from 'svelte-echarts';
    import { init, use } from 'echarts/core';
    import { LineChart } from 'echarts/charts';
    import { ToolboxComponent, DataZoomComponent, GridComponent, TooltipComponent, LegendComponent } from 'echarts/components';
    import { CanvasRenderer } from 'echarts/renderers';

    // Keep the tree-shaking setup local to the component rendering the chart
    use([LineChart, ToolboxComponent, DataZoomComponent, GridComponent, CanvasRenderer, TooltipComponent, LegendComponent]);

    // Accept only the unified options object via Svelte 5 props
    let { options } = $props();
</script>

<div class="card chart" id="price-chart">
    <h3>Electricity Price £ / kWh</h3>
    <div class="chart-area">
        <Chart {init} {options} />
    </div>
</div>

<style>
    .card {
        border: 1px #abc solid;
    }
</style>