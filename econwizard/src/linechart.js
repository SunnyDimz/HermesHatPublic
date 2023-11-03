import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

const LineChart = ({ data }) => {
  const d3Container = useRef(null);

  useEffect(() => {
    if (data && d3Container.current) {
      // Clear the previous SVG
      d3.select(d3Container.current).selectAll("*").remove();

      // Set dimensions and margins for the graph
      const margin = { top: 20, right: 30, bottom: 30, left: 40 },
            width = 460 - margin.left - margin.right,
            height = 400 - margin.top - margin.bottom;

      // Append SVG object to the container
      const svg = d3.select(d3Container.current)
                    .append("svg")
                    .attr("width", width + margin.left + margin.right)
                    .attr("height", height + margin.top + margin.bottom)
                    .append("g")
                    .attr("transform", `translate(${margin.left},${margin.top})`);

      // Add X axis --> it is a date format
      const x = d3.scaleTime()
                  .domain(d3.extent(data, d => new Date(d.date)))
                  .range([0, width]);
      svg.append("g")
         .attr("transform", `translate(0,${height})`)
         .call(d3.axisBottom(x));

      // Add Y axis
      const y = d3.scaleLinear()
                  .domain([0, d3.max(data, d => +d.value)])
                  .range([height, 0]);
      svg.append("g")
         .call(d3.axisLeft(y));

      // Add the line
      svg.append("path")
         .datum(data)
         .attr("fill", "none")
         .attr("stroke", "steelblue")
         .attr("stroke-width", 1.5)
         .attr("d", d3.line()
                      .x(d => x(new Date(d.date)))
                      .y(d => y(d.value))
          );
    }
  }, [data]);

  return (
    <div id="line-chart" ref={d3Container}></div>
  );
};

export default LineChart;
