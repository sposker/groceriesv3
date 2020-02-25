"""

cls ViewFactory

cls ContainerFacotry

cls ItemView:

----

cls TabA
    def populate:
        container = ContainerFacotry['itemview']
        for i in db.items:
            viewlayout =  ViewFactory['itemview'](container, i)
            viewlayout.generate_data()  # Appends data from object to container's data
        container.to_layout()
        self.content.add_widget(container.container)


cls TabB
    def populate:
        for store in db.stores:
            container = ContainerFacotry['loc_map'](store)
            for item in store.locations.items:
                ViewFactory['loc_map'](container, item)

____

cls Root
    on_kv_post:
        tabs = []
        for t in tabs:
            t.populate()
















"""
