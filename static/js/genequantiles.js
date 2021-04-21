
function drawD3(data) {
		$("#d3content").html("");
        var quantileCount = [0, 0, 0, 0];
        var quantileLevel = ["rare","uncommon","common","very common"]
        var quantileCut = [0, 10, 123, 672]
        console.log(data)
        Object.entries(data["drugcount"]).forEach(([key, value]) => {
            pubCount = value["publications"]
            if (pubCount < quantileCut[1]) {
                quantileCount[0] = quantileCount[0] + 1
            }
            else if (pubCount < quantileCut[2]) {
                quantileCount[1] = quantileCount[1] + 1
            }
            else if (pubCount < quantileCut[3]) {
                quantileCount[2] = quantileCount[2] + 1
            }
            else {
                quantileCount[3] = quantileCount[3] + 1
            }
        });

        var margin = { top: 10, right: 0, bottom: 30, left: 0 }
            , width = 800 - margin.left - margin.right // Use the window's width 
            , height = 140 - margin.top - margin.bottom; // Use the window's height

        // 1. Add the SVG to the page and employ #2
        var svg = d3.select("#d3content").append("svg")
            .attr("id", "svg_bars")
            .attr("viewBox", "0 0 750 140")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        
        var barscale = height/(1+Math.max.apply(Math, quantileCount));
        
        for (var i = 0; i < 4; i++) {
            var startLine = 20 + i * 180
            var endLine = (i + 1) * 180

            svg.append("rect")
                .attr("x", startLine+50)
                .attr("y", height-30)
                .attr("width", 60)
                .attr("height", 30)
                .attr('fill', 'grey');


            var bar = svg.append("rect")
                .attr("x", startLine)
                .attr("y", height)
                .attr("width", 160)
                .attr("height", 0)
                .attr('fill', 'dodgerblue');

            var transition = bar.transition().duration(200);
            transition.delay(200).attr("y", height - quantileCount[i]*barscale).attr("height", quantileCount[i]*barscale);
            

            svg.append("line")          // attach a line
                .style("stroke", "black")  // colour the line
                .attr("stroke-width", 3)
                .attr("x1", startLine)     // x position of the first end of the line
                .attr("y1", height)      // y position of the first end of the line
                .attr("x2", endLine)     // x position of the second end of the line
                .attr("y2", height);

            svg.append("line")          // attach a line
                .style("stroke", "black")  // colour the line
                .attr("stroke-width", 3)
                .attr("x1", startLine)     // x position of the first end of the line
                .attr("y1", height + 1)      // y position of the first end of the line
                .attr("x2", startLine)     // x position of the second end of the line
                .attr("y2", height - 14);


            svg.append("line")          // attach a line
                .style("stroke", "black")  // colour the line
                .attr("stroke-width", 3)
                .attr("x1", endLine)     // x position of the first end of the line
                .attr("y1", height + 1)      // y position of the first end of the line
                .attr("x2", endLine)     // x position of the second end of the line
                .attr("y2", height - 14);

            svg.append("text")
                .attr("y", height+20)
                .attr("x", startLine+80)
                .style("text-anchor", "middle")
                .style("font", "18px arial")
                .text(quantileLevel[i]);
            
            svg.append("text")
                .attr("y", height-5)
                .attr("x", startLine+80)
                .style("text-anchor", "middle")
                .style("font", "24px arial")
                .style("fill", "white")
                .text(quantileCount[i]);
            
        }
}