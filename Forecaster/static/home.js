// Calendar
const maxDate = new Date();
maxDate.setDate(maxDate.getDate() + 14);

dateInput.min = new Date().toISOString().split("T")[0];
dateInput.max = maxDate.toISOString().split("T")[0];

// Airport Selected
var code = document.getElementById("code").innerHTML;
const select = document.querySelector("select");
select.value = code;

// Main Gauge
function setGaugeValue(gauge, value) {
  if (value < 0) {
    value = 0;
  } else if (value > 1) {
    value = 1;
  }
  gauge.querySelector(".gauge__fill").style.transform = `rotate(${value / 2}turn)`;
  gauge.querySelector(".gauge__cover").textContent = `${Math.round(value * 100)}%`;
};

const gaugeElement = document.querySelector(".gauge");
var rate = document.getElementById("rate").innerHTML;
var conv_rate = parseFloat(rate);
setGaugeValue(gaugeElement, conv_rate);

// Recommend Gauge
function setMinGaugeValue(min_gauge, min_value) {
  if (min_value < 0) {
    min_value = 0;
  } else if (min_value > 1) {
    min_value = 1;
  }
  min_gauge.querySelector(".min_gauge__fill").style.transform = `rotate(${min_value / 2}turn)`;
  min_gauge.querySelector(".min_gauge__cover").textContent = `${Math.round(min_value * 100)}%`;
};

const min_gaugeElement = document.querySelector(".min_gauge");
var min_rate = document.getElementById("min_rate").innerHTML;
var conv_min_rate = parseFloat(min_rate);
setMinGaugeValue(min_gaugeElement, conv_min_rate);

// Horizontal Bar Chart
var date_title = document.getElementById("ddtm").innerHTML;

function adjustRate(airport_rate) {
    var res = Math.round(parseFloat(document.getElementById(airport_rate).innerHTML) * 100);
    if (res < 0) {
        res = 0;
    } else if (res > 100) {
        res = 100;
    }
    return res;
}

var atl_rate = adjustRate('atl_rate');
var lax_rate = adjustRate('lax_rate');
var ord_rate = adjustRate('ord_rate');
var dfw_rate = adjustRate('dfw_rate');
var den_rate = adjustRate('den_rate');
var jfk_rate = adjustRate('jfk_rate');
var sfo_rate = adjustRate('sfo_rate');
var las_rate = adjustRate('las_rate');
var sea_rate = adjustRate('sea_rate');
var clt_rate = adjustRate('clt_rate');

const sample = [
  {
    airport: 'ATL',
    value: atl_rate
  },
  {
    airport: 'LAX',
    value: lax_rate
  },
  {
    airport: 'ORD',
    value: ord_rate
  },
  {
    airport: 'DFW',
    value: dfw_rate
  },
  {
    airport: 'DEN',
    value: den_rate
  },
  {
    airport: 'JFK',
    value: jfk_rate
  },
  {
    airport: 'SFO',
    value: sfo_rate
  },
  {
    airport: 'LAS',
    value: las_rate
  },
  {
    airport: 'SEA',
    value: sea_rate
  },
  {
    airport: 'CLT',
    value: clt_rate
  }
];

sample.sort(function(a, b) {
    return a.value - b.value;
    });

const svg = d3.select('svg');
const svgContainer = d3.select('#container');

const margin = 70;
const width = 720 - 2 * margin;
const height = 480 - 2 * margin;

const chart = svg.append('g')
  .attr('transform', `translate(${margin}, ${margin})`);

const xScale = d3.scaleBand()
  .range([0, width])
  .domain(sample.map((s) => s.airport))
  .padding(0.4)

const yScale = d3.scaleLinear()
  .range([height, 0])
  .domain([0, 100]);

const makeYLines = () => d3.axisLeft()
  .scale(yScale)

chart.append('g')
  .attr('transform', `translate(0, ${height})`)
  .call(d3.axisBottom(xScale));

chart.append('g')
  .call(d3.axisLeft(yScale));

chart.append('g')
  .attr('class', 'grid')
  .call(makeYLines()
    .tickSize(-width, 0, 0)
    .tickFormat('')
  )

const barGroups = chart.selectAll()
  .data(sample)
  .enter()
  .append('g')

barGroups
  .append('rect')
  .attr('class', 'bar')
  .attr('style', function(c) {if (c.airport == code) { return 'fill:lightcoral;'} else { return 'fill:teal;'}})
  .attr('x', (g) => xScale(g.airport))
  .attr('y', (g) => yScale(g.value))
  .attr('height', (g) => height - yScale(g.value))
  .attr('width', xScale.bandwidth())
  .on('mouseenter', function (actual, i) {
    d3.selectAll('.value')
      .attr('opacity', 0)

    d3.select(this)
      .transition()
      .duration(300)
      .attr('opacity', 0.6)
      .attr('x', (a) => xScale(a.airport) - 5)
      .attr('width', xScale.bandwidth() + 10)

    const y = yScale(actual.value)

    line = chart.append('line')
      .attr('id', 'limit')
      .attr('x1', 0)
      .attr('y1', y)
      .attr('x2', width)
      .attr('y2', y)

    barGroups.append('text')
      .attr('class', 'divergence')
      .attr('x', (a) => xScale(a.airport) + xScale.bandwidth() / 2)
      .attr('y', (a) => yScale(a.value) + 30)
      .attr('fill', 'white')
      .attr('text-anchor', 'middle')
      .text((a, idx) => {
        const divergence = (a.value - actual.value).toFixed()

        let text = ''
        if (divergence > 0) text += '+'
        text += `${divergence}%`

        return idx !== i ? text : '';
      })

  })
  .on('mouseleave', function () {
    d3.selectAll('.value')
      .attr('opacity', 1)

    d3.select(this)
      .transition()
      .duration(300)
      .attr('opacity', 1)
      .attr('x', (a) => xScale(a.airport))
      .attr('width', xScale.bandwidth())

    chart.selectAll('#limit').remove()
    chart.selectAll('.divergence').remove()
  })

barGroups
  .append('text')
  .attr('class', 'value')
  .attr('x', (a) => xScale(a.airport) + xScale.bandwidth() / 2)
  .attr('y', (a) => yScale(a.value) + 30)
  .attr('text-anchor', 'middle')
  .text((a) => `${a.value}%`)

svg
  .append('text')
  .attr('class', 'label')
  .attr('x', -(height / 2) - margin)
  .attr('y', margin / 2.4)
  .attr('transform', 'rotate(-90)')
  .attr('text-anchor', 'middle')
  .text('Delay Probability (%)')

svg.append('text')
  .attr('class', 'label')
  .attr('x', width / 2 + margin)
  .attr('y', height + margin * 1.7)
  .attr('text-anchor', 'middle')
  .text('Airport')

svg.append('text')
  .attr('class', 'title')
  .attr('x', width / 2 + margin)
  .attr('y', 40)
  .attr('text-anchor', 'middle')
  .text('Delay Probability by Airport for '+date_title)

// Scatterplot
var sd = d3.timeParse("%Y-%m-%d")(document.getElementById("sd").innerHTML);
var rd = d3.timeParse("%m/%d/%Y")(document.getElementById("rd").innerHTML);
let compareTime = d3.timeFormat("%Y-%m-%d");

var sp_margin = 30,
    sp_width = 460 - sp_margin * 2,
    sp_height = 400 - sp_margin * 2;

var sp_svg= d3.select("#plot")
  .append("svg")
    .attr("width", sp_width + sp_margin * 2)
    .attr("height", sp_height + sp_margin * 2)
  .append("g")
    .attr("transform",
          "translate(" + sp_margin + "," + sp_margin + ")");

d3.csv('static/delay.csv?t=' + Date.now(),
  function(d){
    return { date : d3.timeParse("%Y-%m-%d")(d.date), value : Math.round(parseFloat(d.value)*100) }
  },

  function(data) {
    var x = d3.scaleTime()
      .domain(d3.extent(data, function(d) { return d.date; }))
      .range([ 10, sp_width ]);
    sp_svg.append("g")
      .attr("transform", "translate(0," + sp_height + ")")
      .call(d3.axisBottom(x).tickFormat(d3.timeFormat("%b %d")))

    var y = d3.scaleLinear()
      .domain( [0, 100])
      .range([ sp_height, 30 ]);
    sp_svg.append("g")
      .attr("transform", "translate(10,0)")
      .call(d3.axisLeft(y).tickFormat(d => d+"%"));

    const makeXLines = () => d3.axisBottom()
      .scale(x)
      sp_svg.append('g')
      .attr('class', 'grid')
      .attr('transform', `translate(0, ${sp_height})`)
      .call(makeXLines()
        .ticks(11)
        .tickSize(-sp_height+30, 0, 0)
        .tickFormat('')
      )

    sp_svg.append("path")
      .datum(data)
      .attr("fill", "none")
      .attr("stroke", "black")
      .attr("stroke-width", 1.5)
      .attr("d", d3.line()
        .x(function(d) { return x(d.date) })
        .y(function(d) { return y(d.value) })
        )

    var Tooltip = d3.select("#plot")
      .append("div")
      .style("opacity", 0)
      .attr("class", "tooltip")
      .style("background-color", "lightyellow")
      .style("border", "solid")
      .style("border-color", "gray")
      .style("border-width", "1.5px")
      .style("border-radius", "5px")
      .style("padding", "5px")
      .style("width", "fit-content")

      var mouseover = function(d) {
        Tooltip
          .style("opacity", 1)
          .attr("r", 9)

        d3.select(this)
            .transition()
            .duration(300)
            .attr('r', 10)
      }

      let formatTime = d3.timeFormat("%b %d, %Y");
      var mousemove = function(d) {
        Tooltip
          .html(formatTime(d.date) + ": " + d.value + "%")
          .style("left", (d3.mouse(this)[0]+40) + "px")
          .style("top", (d3.mouse(this)[1]) + "px")
      }
      var mouseleave = function(d) {
        Tooltip
          .style("opacity", 0)

        d3.select(this)
          .transition()
          .duration(300)
          .attr('r', 6)
      }

    sp_svg
      .append("g")
      .selectAll("dot")
      .data(data)
      .enter()
      .append("circle")
        .attr("class", "myCircle")
        .attr("cx", function(d) { return x(d.date) } )
        .attr("cy", function(d) { return y(d.value) } )
        .attr("r", 6)
        .attr("stroke", function(c) {if (compareTime(c.date) == compareTime(sd)) { return 'lightcoral' } else if (compareTime(c.date) == compareTime(rd)) { return 'skyblue' } else { return 'teal'}})
        .attr("stroke-width", 3)
        .attr("fill", "white")
        .on("mouseover", mouseover)
        .on("mousemove", mousemove)
        .on("mouseleave", mouseleave)

    sp_svg.append('text')
      .attr('class', 'title')
      .attr('x', sp_width / 2)
      .attr('y', 0)
      .attr('text-anchor', 'middle')
      .text('Delay Probability by Date for ' + code)
})
