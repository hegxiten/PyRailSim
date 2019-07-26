warning: LF will be replaced by CRLF in OOD_Train/.ipynb_checkpoints/Untitled-checkpoint.ipynb.
The file will have its original line endings in your working directory.
warning: LF will be replaced by CRLF in OOD_Train/Untitled.ipynb.
The file will have its original line endings in your working directory.
[1mdiff --git a/OOD_Train/.ipynb_checkpoints/Untitled-checkpoint.ipynb b/OOD_Train/.ipynb_checkpoints/Untitled-checkpoint.ipynb[m
[1mindex 0f444e5..18e7c6a 100644[m
[1m--- a/OOD_Train/.ipynb_checkpoints/Untitled-checkpoint.ipynb[m
[1m+++ b/OOD_Train/.ipynb_checkpoints/Untitled-checkpoint.ipynb[m
[36m@@ -26,17 +26,17 @@[m
    "metadata": {},[m
    "outputs": [],[m
    "source": [[m
[31m-    "_node = {  0:CtrlPoint(idx=0, ports=[0,1], MP=0.0), \\\n",[m
[31m-    "                    1:AutoPoint(1), \\\n",[m
[31m-    "                    2:AutoPoint(2), \\\n",[m
[31m-    "                    3:CtrlPoint(idx=3, ports=[0,1,3], ban_routes={1:[3],3:[1]}), \\\n",[m
[31m-    "                    4:CtrlPoint(idx=4, ports=[0,2,1], ban_routes={0:[2],2:[0]}), \\\n",[m
[31m-    "                    5:AutoPoint(5), \\\n",[m
[31m-    "                    6:CtrlPoint(idx=6, ports=[0,1,3], ban_routes={1:[3],3:[1]}), \\\n",[m
[31m-    "                    7:CtrlPoint(idx=7, ports=[0,2,1], ban_routes={0:[2],2:[0]}), \\\n",[m
[31m-    "                    8:AutoPoint(8), \\\n",[m
[31m-    "                    9:AutoPoint(9), \\\n",[m
[31m-    "                    10:CtrlPoint(idx=10, ports=[0,1])}       \n",[m
[32m+[m[32m    "_node = { 0:CtrlPoint(idx=0, ports=[0,1], MP=0.0), \\\n",[m
[32m+[m[32m    "            1:AutoPoint(1), \\\n",[m
[32m+[m[32m    "            2:AutoPoint(2), \\\n",[m
[32m+[m[32m    "            3:CtrlPoint(idx=3, ports=[0,1,3], ban_ports_by_port={1:[3],3:[1]}), \\\n",[m
[32m+[m[32m    "            4:CtrlPoint(idx=4, ports=[0,2,1], ban_ports_by_port={0:[2],2:[0]}), \\\n",[m
[32m+[m[32m    "            5:AutoPoint(5), \\\n",[m
[32m+[m[32m    "            6:CtrlPoint(idx=6, ports=[0,1,3], ban_ports_by_port={1:[3],3:[1]}), \\\n",[m
[32m+[m[32m    "            7:CtrlPoint(idx=7, ports=[0,2,1], ban_ports_by_port={0:[2],2:[0]}), \\\n",[m
[32m+[m[32m    "            8:AutoPoint(8), \\\n",[m
[32m+[m[32m    "            9:AutoPoint(9), \\\n",[m
[32m+[m[32m    "            10:CtrlPoint(idx=10, ports=[0,1])}       \n",[m
     "nbunch = [_node[i] for i in range(len(_node))]\n",[m
     "\n",[m
     "_track = [  Track(nbunch[0], 1, nbunch[1], 0), Track(nbunch[1], 1, nbunch[2], 0), Track(nbunch[2], 1, nbunch[3], 0),\\\n",[m
[36m@@ -68,7 +68,7 @@[m
   },[m
   {[m
    "cell_type": "code",[m
[31m-   "execution_count": 6,[m
[32m+[m[32m   "execution_count": 3,[m
    "metadata": {},[m
    "outputs": [],[m
    "source": [[m
[36m@@ -125,20 +125,191 @@[m
   },[m
   {[m
    "cell_type": "code",[m
[31m-   "execution_count": 7,[m
[32m+[m[32m   "execution_count": 12,[m
    "metadata": {},[m
    "outputs": [],[m
    "source": [[m
     "F[_node[0]][_node[3]][0]['instance'].traffic_direction = 'east'"[m
    ][m
   },[m
[32m+[m[32m  {[m
[32m+[m[32m   "cell_type": "code",[m
[32m+[m[32m   "execution_count": 13,[m
[32m+[m[32m   "metadata": {},[m
[32m+[m[32m   "outputs": [[m
[32m+[m[32m    {[m
[32m+[m[32m     "data": {[m
[32m+[m[32m      "text/plain": [[m
[32m+[m[32m       "'east'"[m
[32m+[m[32m      ][m
[32m+[m[32m     },[m
[32m+[m[32m     "execution_count": 13,[m
[32m+[m[32m     "metadata": {},[m
[32m+[m[32m     "output_type": "execute_result"[m
[32m+[m[32m    }[m
[32m+[m[32m   ],[m
[32m+[m[32m   "source": [[m
[32m+[m[32m    "G[_node[0]][_node[1]][0]['instance'].traffic_direction"[m
[32m+[m[32m   ][m
[32m+[m[32m  },[m
[32m+[m[32m  {[m
[32m+[m[32m   "cell_type": "code",[m
[32m+[m[32m   "execution_count": 7,[m
[32m+[m[32m   "metadata": {},[m
[32m+[m[32m   "outputs": [[m
[32m+[m[32m    {[m
[32m+[m[32m     "data": {[m
[32m+[m[32m      "text/plain": [[m
[32m+[m[32m       "{'attr': {'_observers': [AutoPoint2, CtrlPoint4],\n",[m
[32m+[m[32m       "  'idx': 3,\n",[m
[32m+[m[32m       "  'type': 'cp',\n",[m
[32m+[m[32m       "  'MP': 15.0,\n",[m
[32m+[m[32m       "  'ports': [0, 1, 3],\n",[m
[32m+[m[32m       "  'signal_by_port': defaultdict(list,\n",[m
[32m+[m[32m       "              {0: HomeSignal of CtrlPoint3, port: 0,\n",[m
[32m+[m[32m       "               1: HomeSignal of CtrlPoint3, port: 1,\n",[m
[32m+[m[32m       "               3: HomeSignal of CtrlPoint3, port: 3}),\n",[m
[32m+[m[32m       "  'available_ports_by_port': defaultdict(list, {0: [1, 3], 1: [0], 3: [0]}),\n",[m
[32m+[m[32m       "  'non_mutex_routes_by_route_by_route': defaultdict(list, {}),\n",[m
[32m+[m[32m       "  'track_by_port': defaultdict(int,\n",[m
[32m+[m[32m       "              {0: Track MP: 10.0 to MP: 15.0 idx: 0,\n",[m
[32m+[m[32m       "               1: Track MP: 15.0 to MP: 20.0 idx: 0,\n",[m
[32m+[m[32m       "               3: Track MP: 15.0 to MP: 20.0 idx: 1}),\n",[m
[32m+[m[32m       "  'neighbors': [AutoPoint2, CtrlPoint4],\n",[m
[32m+[m[32m       "  '_current_routes': [],\n",[m
[32m+[m[32m       "  'all_valid_routes': [],\n",[m
[32m+[m[32m       "  'ban_ports_by_port': {1: [3], 3: [1]}},\n",[m
[32m+[m[32m       " 'instance': CtrlPoint3}"[m
[32m+[m[32m      ][m
[32m+[m[32m     },[m
[32m+[m[32m     "execution_count": 7,[m
[32m+[m[32m     "metadata": {},[m
[32m+[m[32m     "output_type": "execute_result"[m
[32m+[m[32m    }[m
[32m+[m[32m   ],[m
[32m+[m[32m   "source": [[m
[32m+[m[32m    "G.node[_node[3]]"[m
[32m+[m[32m   ][m
[32m+[m[32m  },[m
[32m+[m[32m  {[m
[32m+[m[32m   "cell_type": "code",[m
[32m+[m[32m   "execution_count": 9,[m
[32m+[m[32m   "metadata": {},[m
[32m+[m[32m   "outputs": [[m
[32m+[m[32m    {[m
[32m+[m[32m     "data": {[m
[32m+[m[32m      "text/plain": [[m
[32m+[m[32m       "2393026156920"[m
[32m+[m[32m      ][m
[32m+[m[32m     },[m
[32m+[m[32m     "execution_count": 9,[m
[32m+[m[32m     "metadata": {},[m
[32m+[m[32m     "output_type": "execute_result"[m
[32m+[m[32m    }[m
[32m+[m[32m   ],[m
[32m+[m[32m   "source": [[m
[32m+[m[32m    "id(G.node[_node[3]]['instance'].signal_by_port[3].cp)"[m
[32m+[m[32m   ][m
[32m+[m[32m  },[m
   {[m
    "cell_type": "code",[m
    "execution_count": 10,[m
    "metadata": {},[m
[31m-   "outputs": [],[m
[32m+[m[32m   "outputs": [[m
[32m+[m[32m    {[m
[32m+[m[32m     "data": {[m
[32m+[m[32m      "text/plain": [[m
[32m+[m[32m       "2393026156920"[m
[32m+[m[32m      ][m
[32m+[m[32m     },[m
[32m+[m[32m     "execution_count": 10,[m
[32m+[m[32m     "metadata": {},[m
[32m+[m[32m     "output_type": "execute_result"[m
[32m+[m[32m    }[m
[32m+[m[32m   ],[m
[32m+[m[32m   "source": [[m
[32m+[m[32m    "id(G.node[_node[3]]['instance'])"[m
[32m+[m[32m   ][m
[32m+[m[32m  },[m
[32m+[m[32m  {[m
[32m+[m[32m   "cell_type": "code",[m
[32m+[m[32m   "execution_count": 11,[m
[32m+[m[32m   "metadata": {},[m
[32m+[m[32m   "outputs": [[m
[32m+[m[32m    {[m
[32m+[m[32m     "data": {[m
[32m+[m[32m      "text/plain": [[m
[32m+[m[32m       "{'attr': {'_observers': [AutoPoint2, CtrlPoint4],\n",[m
[32m+[m[32m       "  'idx': 3,\n",[m
[32m+[m[32m       "  'type': 'cp',\n",[m
[32m+[m[32m       "  'MP': 15.0,\n",[m
[32m+[m[32m       "  'ports': [0, 1, 3],\n",[m
[32m+[m[32m       "  'signal_by_port': defaultdict(list,\n",[m
[32m+[m[32m       "              {0: HomeSignal of CtrlPoint3, port: 0,\n",[m
[32m+[m[32m       "               1: HomeSignal of CtrlPoint3, port: 1,\n",[m
[32m+[m[32m       "               3: HomeSignal of CtrlPoint3, port: 3}),\n",[m
[32m+[m[32m       "  'available_ports_by_port': defaultdict(list, {0: [1, 3], 1: [0], 3: [0]}),\n",[m
[32m+[m[32m       