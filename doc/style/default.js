$(document).ready(function() {

    function nodeData(node, count, level) {
        return {
            label: count + " " + node.text(),
            id: node.attr('id'),
            level: level
        };
    }

    var data = [];


    var countH1 = 0, countH2 = 0, countH3 = 0;

    $('h1[id]').each(function() {
        var h1data, h2data = [];

        countH1 += 1;

        $(this).nextUntil('h1', 'h2').each(function() {
            countH2 += 1;
            h2node = nodeData($(this), countH1 + "." + countH2, 2);

            var h3data = [];

            $(this).nextUntil('h1,h2', 'h3').each(function() {
                countH3 += 1;
                h3data.push(nodeData($(this), countH1 + "." + countH2 + "." + countH3, 3));
            });

            countH3 = 0;
            h2node.children = h3data;
            h2data.push(h2node);


        });
        countH2 = 0;

        h1data = nodeData($(this), countH1, 1);
        h1data.children = h2data;


        data.push(h1data);
    });


    var $tree = $("DIV.navtree");
    $tree.tree({
        data: data
    });
    $('DIV.navtree').bind("tree.click", function(event) {
        var node = event.node;
        var top = document.getElementById(node.id).offsetTop;
        window.scrollTo(0, top);
        $tree.tree('openNode', node);
        event.preventDefault();
    });

    $(".navtools").bind("click", function(e) {
        if (e.srcElement === $(".nt-all")) {

        }

        function walkNodes(rootNode, fn) {
            if (rootNode.children) {
                $.each(rootNode.children, function(index, node) {
                    fn.apply(this, [node]);
                    walkNodes(node, fn);
                });
            }
        }

        walkNodes($tree.tree("getTree"), function(node) {
            if (e.target.id === "nt-all") {
                $tree.tree('openNode', node);
            }
            if (e.target.id === "nt-none") {
                $tree.tree('closeNode', node);
            }
            if (e.target.id.substring(0, 4) === "nt-l") {
                var selectedLevel = parseInt(e.target.id.substring(4, 5), 10);
                if (node.level < selectedLevel) {
                    $tree.tree('openNode', node);
                } else {
                    $tree.tree('closeNode', node);
                }
            }


        });



    });

});


