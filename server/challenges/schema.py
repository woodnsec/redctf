import graphene
import rethinkdb as r
import re
from dockerAPI.dockerAPI import *
from rethinkdb.errors import RqlRuntimeError, RqlDriverError
from redctf.settings import RDB_HOST, RDB_PORT, CTF_DB
from graphene_django import DjangoObjectType
from graphene_file_upload.scalars import Upload
from django.utils.dateformat import format
from users.validators import validate_user_is_admin, validate_user_is_authenticated
from challenges.validators import validate_flag, validate_flag_unique, validate_points, validate_title, validate_description, validate_imageName, validate_ports, validate_pathPrefix, validate_pathPrefix_unique
from categories.validators import validate_category_exists
from categories.models import Category
from challenges.models import Challenge
from teams.models import SolvedChallenge

d = dockerAPI()

class AddChallenge(graphene.Mutation):
    status = graphene.String()

    class Arguments:
        category = graphene.Int(required=True)
        title = graphene.String(required=True)
        points = graphene.Int(required=True)
        description = graphene.String(required=True)
        flag = graphene.String(required=True)
        hosted = graphene.Boolean(required=True)
        image_name = graphene.String(required=False)
        ports = graphene.String(required=False)
        #path_prefix = graphene.String(required=False)
        upload = Upload(required=False)

    #def mutate(self, info, category, title, points, description, flag, hosted, image_name, ports, path_prefix, upload=None):
    def mutate(self, info, category, title, points, description, flag, hosted, ports, image_name=None, upload=None):
        user = info.context.user
        # Validate user is admin
        validate_user_is_admin(user)

        # TODO: sanitize all the input fields 
        validate_flag(flag)
        validate_flag_unique(flag)
        validate_points(points)
        validate_title(title)
        validate_description(description)
        validate_category_exists(category)
        if image_name:
            validate_imageName(image_name)
        if ports:
            validate_ports(ports)
        # if path_prefix:
        #     validate_pathPrefix(path_prefix)
        #     validate_pathPrefix_unique(path_prefix)

        #parse dockerfile for list of ports
        if upload:
            try:
                ports = list()
                for line in upload:
                    line = line.decode('utf-8')
                    start = 'EXPOSE '

                    if (start in line):
                        possible_port = (line[line.find(start)+len(start):])
                        ports.append(possible_port.split())

                # flatten list
                flattened_ports = list(set([val for sublist in ports for val in sublist]))
                print (flattened_ports)

            except Exception as e:
                raise Exception('Error parsing uploaded Dockerfile: ', e)


        challenge_category = Category.objects.get(id=category)

        # Save the challenge flag to the database
        challenge = Challenge(category=challenge_category, title=title, description=description, flag=flag, points=points, hosted=hosted, imageName=image_name, ports=ports)
        challenge.save()

        #set var for pathPrefix and tag
        path_tag = str(challenge.id) + '_' + re.sub('[^A-Za-z0-9]+', '', challenge.category.name.lower()) + str(challenge.points)
        challenge.pathPrefix = path_tag
        
        if upload:
            image_name = path_tag + ':latest'

            #build image
            build = d.buildImage(fileobj=upload.file, tag=path_tag)
        
            #delete already saved challenge if build fails
            if not build:
                chall_id = challenge.id
                try:
                    challenge.delete()
                except:
                    #raise exception if unable to delete already saved challenge requiring manual intervention
                    raise Exception('Unable to delete challenge ID: %i. Manual deletion necessary.' % (chall_id))

                raise Exception('Unable to build image.  Reverted challenge creation.')

            challenge.upload = upload
            challenge.imageName = image_name
        
        challenge.save()


        # Push the realtime data to rethinkdb
        connection = r.connect(host=RDB_HOST, port=RDB_PORT)
        try:
            r.db(CTF_DB).table('challenges').insert({ 'sid': challenge.id, 'category': challenge.category.id, 'title': title, 'points': points, 'description': description, 'hosted': hosted, 'imageName': image_name, 'ports': ports, 'pathPrefix':path_tag, 'created': format(challenge.created, 'U')}).run(connection)
        except RqlRuntimeError as e:
            raise Exception('Error adding challenge to realtime database: %s' % (e))
        finally:
            connection.close()

        return AddChallenge(status='Challenge Created')



class CheckFlag(graphene.Mutation):
    status = graphene.String()

    class Arguments:
        flag = graphene.String(required=True)

    def mutate(self, info, flag):
        user = info.context.user
        # Validate user is authenticated
        validate_user_is_authenticated(user)

        # Sanitize flag input 
        validate_flag(flag)

        correct = False
        if Challenge.objects.filter(flag__iexact=flag).exists():
            chal = Challenge.objects.get(flag__iexact=flag)
            if chal.id not in user.team.solved.all().values_list('challenge_id', flat=True):
                user.team.points += chal.points
                user.team.correct_flags += 1
                sc = SolvedChallenge(challenge=chal)
                sc.save()
                user.team.solved.add(sc)
                user.team.save()
            correct = True
        else:
            user.team.wrong_flags += 1    
            user.team.save()
            correct = False

        # Create list of solved challenges
        solved = []
        for sc in user.team.solved.all().order_by('timestamp'):
            solved.append({'id': sc.challenge.id, 'points': sc.challenge.points, 'timestamp': format(sc.timestamp, 'U')})
             
        # Push the realtime data to rethinkdb
        connection = r.connect(host=RDB_HOST, port=RDB_PORT)
        try:
            r.db(CTF_DB).table('teams').filter({"sid": user.team.id}).update({'points': user.team.points, 'correct_flags': user.team.correct_flags, 'wrong_flags': user.team.wrong_flags, 'solved': solved}).run(connection)
            if correct:
                r.db(CTF_DB).table('challenges').filter({"sid": chal.id}).update({'solved_count': SolvedChallenge.objects.filter(challenge=chal).count()}).run(connection)
        except RqlRuntimeError as e:
            raise Exception('Error adding category to realtime database: %s' % (e))
        finally:
            connection.close()
        
        if correct:
            return CheckFlag(status='Correct Flag') 
        else:
            return CheckFlag(status='Wrong Flag')
        
class DeleteChallenge(graphene.Mutation):
    status = graphene.String()

    class Arguments:
        id = graphene.Int(required=True)

    def mutate(self, info, id):
        user = info.context.user
        # Validate user is admin
        validate_user_is_admin(user)
        

        # ID is primary key for django, SID is PK in Rethink
        if Challenge.objects.filter(id__iexact=id).exists():
            chal = Challenge.objects.get(id__iexact=id)
            chal.delete()

        else:
            return DeleteChallenge(status='Error deleting challenge from database: %s' % (id))
            
        connection = r.connect(host=RDB_HOST, port=RDB_PORT)
        try:
            r.db(CTF_DB).table('challenges').filter({'sid':id}).delete().run(connection)
        except RqlRuntimeError as e:
            raise Exception('Error deleting challenge from realtime database: %s' % (e))
        finally:
            connection.close()

        return DeleteChallenge(status='Challenge Deleted: %s' % (id))
    
class UpdateChallenge(graphene.Mutation):
    status = graphene.String()

    class Arguments:
        id = graphene.Int(required=True)
        category = graphene.Int(required=False)
        title = graphene.String(required=False)
        points = graphene.Int(required=False)
        description = graphene.String(required=False)
        flag = graphene.String(required=False)
        hosted = graphene.Boolean(required=False)
        image_name = graphene.String(required=False)
        ports = graphene.String(required=False)
        path_prefix = graphene.String(required=False)
        upload = Upload(required=False)
        

    def mutate(self, info, id, category=None, title=None, points=None, description=None, flag=None, hosted=None, image_name=None, ports=None, path_prefix=None, upload=None):
        user = info.context.user
        # Validate user is admin
        validate_user_is_admin(user)
        

        rethink_updates = {}
        
        
        if Challenge.objects.filter(id__iexact=id).exists():
            chal = Challenge.objects.get(id__iexact=id)
            if title:
                chal.title = title
                rethink_updates['title'] = title
                
            if category:
                challenge_category = Category.objects.get(id=category)
                chal.category = challenge_category
                rethink_updates['category'] = category
                        
            if points:
                chal.points = points
                rethink_updates['points'] = points
                
            if description:
                chal.description = description
                rethink_updates['description'] = description
                
            if flag:
                chal.flag = flag
                rethink_updates['flag'] = flag
                
            if hosted:
                chal.hosted = hosted
                rethink_updates['hosted'] = hosted
                
            if image_name:
                chal.imageName = image_name
                rethink_updates['imageName'] = image_name
                
            if ports:
                chal.ports = ports
                rethink_updates['ports'] = ports
            
            if path_prefix:
                chal.pathPrefix = path_prefix
                rethink_updates['pathPrefix'] = path_prefix
            
            
            if upload:
                try:
                    ports = list()
                    for line in upload:
                        line = line.decode('utf-8')
                        start = 'EXPOSE '

                        if (start in line):
                            possible_port = (line[line.find(start)+len(start):])
                            ports.append(possible_port.split())

                    # flatten list
                    flattened_ports = list(set([val for sublist in ports for val in sublist]))
                    print (flattened_ports)
                    chal.ports = flattened_ports
                    chal.upload = upload
                    rethink_updates['upload'] = upload
                    
                except Exception as e:
                    raise Exception('Error parsing uploaded Dockerfile: ', e)
                
            
            chal.save()
            
            
        else:
            # TODO: updates broken. it updates the challenge and adds the new one called title with value title 
            return UpdateChallenge(status='Error updating challenge')
        # updates = {'title':updatedTitle}
        connection = r.connect(host=RDB_HOST, port=RDB_PORT)
        try:
            r.db(CTF_DB).table('challenges').filter({'sid':id}).update(rethink_updates).run(connection)
        except RqlRuntimeError as e:
            raise Exception('Error updating challenge from realtime database: %s' % (e))
        finally:
            connection.close()

        return UpdateChallenge(status='Challenge Updated: %s' % (id))





class Mutation(graphene.ObjectType):
    add_challenge = AddChallenge.Field()
    check_flag = CheckFlag.Field()
    delete_challenge = DeleteChallenge.Field()
    update_challenge = UpdateChallenge.Field()