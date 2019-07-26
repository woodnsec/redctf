import graphene
import rethinkdb as r
import dockerAPI
from rethinkdb.errors import RqlRuntimeError, RqlDriverError
from redctf.settings import RDB_HOST, RDB_PORT, CTF_DB
from containers.models import Container
from users.validators import validate_user_is_admin
from containers.validators import validate_name, validate_name_unique

d = dockerAPI()

class AddContainer(graphene.Mutation):
	status = graphene.String()

	class Arguments:
		name = graphene.String(required=True)

	def mutate(self, info, name):
		user = info.context.user
		image = info.context.image
		port = info.context.port
		path = info.context.path
		# TODO: set this to take network parameter, if they want to do user isolation vs just container isolation
		# net = info.context.net
		net = 'false'
		# Validate user is admin
		validate_user_is_admin(user)

		# Sanitize inputs
		validate_name(name)
		validate_name_unique(name)

		# Save the container
		container = Container(name=name)
		container.save()

		# Push the realtime data to rethinkdb
		# TODO: does this need to be done?? Should it be a call to the systems instead?
		connection = r.connect(host=RDB_HOST, port=RDB_PORT)
		try:
			r.db(CTF_DB).table('categories').insert(
				{'sid': container.id, 'name': container.name, 'created': format(container.created, 'U')}).run(connection)
		except RqlRuntimeError as e:
			raise Exception('Error adding container to realtime database: %s' % (e))
		finally:
			connection.close()
		# TODO: does this belong above the DB connection? It should log what the connection details are for the DB.
		try:
			dockerConnection = d.createContainer(username=user, imageName=image, port=port, pathPrefix=path, netIsolation=net)
		except:
			print('test error')

		return AddContainer(status='Container Created')

class Mutation(graphene.ObjectType):
	add_container = AddContainer.Field()