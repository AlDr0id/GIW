% include('header.tpl', title='Info')
<h1>Municipios de Madrid</h1>
	<ul>
	% for m in mun:
		<li>{{m}}</li>
	%end
	</ul>
	<a href="..">Volver</a>
% include('footer.tpl')
